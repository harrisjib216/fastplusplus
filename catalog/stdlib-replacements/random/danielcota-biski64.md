# biski64

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [C++ standard library replacements](../README.md) › [Random numbers](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟡 stale

> Tiny 3-word Weyl+rotate PRNG beating std::mt19937_64 on raw throughput; not a drop-in, ships as Rust crate + C reference source.

| | |
|---|---|
| **Beats** | std::mt19937, std::mt19937_64 |
| **Claimed result** | \~2.5x biski64 vs std::mt19937_64 (13.8-14.0 GB/s median/mean vs 5.54-5.63 GB/s), \~2.8x vs std::mt19937 (5.01-5.02 GB/s) (derived from page data: results/prng-next-benchmark.json, 'threads:7' mean/median aggregates) |
| **Workload** | Raw PRNG next()-call throughput for 64-bit generators, measured with Google Benchmark using 7 threads (nproc-1 on an 8-vCPU VM), 5 repetitions with random interleaving; reported bytes_per_second is per thread, in the planet36/prng-test-bench harness. |
| **Metric** | throughput |
| **Hardware** | 8-vCPU VM (hostname 'arch-vm'), 2419 MHz, 32 KiB L1d / 4 MiB L2 / 36 MiB L3 per benchmark JSON context; exact CPU model not stated |
| **Compiler and flags** | g++ (version not stated), -std=c++26 -O3 -flto=auto -march=native (per repo Makefile); Google Benchmark v1.9.5 release build |
| **Adoption** | 152 stars; published as the biski64 crate on crates.io |
| **Last commit** | 2025-06-12 |
| **Links** | [repository](https://github.com/danielcota/biski64) · [benchmark](https://github.com/planet36/prng-test-bench/blob/main/results/prng-next-benchmark.json) |

## Verdict

In planet36/prng-test-bench's Google Benchmark harness (7 threads on an 8-vCPU VM, g++ -O3 -flto=auto -march=native, C++26), that harness's own C++ port of biski64 sustained 13.8 GB/s median / 14.0 GB/s mean per-thread next()-call throughput versus 5.63/5.54 GB/s for libstdc++'s std::mt19937_64 (\~2.5x) and 5.01/5.02 GB/s for std::mt19937 (\~2.8x). biski64's own README instead benchmarks against xoshiro/PCG/wyrand/sfc64/Java generators on an AMD Ryzen 9 7950X3D and does not include std::mt19937.

## Use it when

- Non-cryptographic, throughput-bound 64-bit generation (simulation, sampling, shuffling) where you'd otherwise use std::mt19937_64 and want a smaller/faster algorithm to port in.
- Rust projects on rand_core/rand 0.9 wanting a no_std-compatible RngCore/SeedableRng implementation via the biski64 crate.
- Parallel workloads needing independent streams from one seed: biski64_stream()/from_seed_for_stream() space fast_loop per stream without a separate jump-ahead call.
- Memory- or register-constrained targets: 3 x 64-bit words of state; a user reports it running on an ESP32 (issue #11).
- You've already accepted a Weyl-sequence design's 2^64 minimum period as sufficient for the workload.

## Skip it when

- You need a literal drop-in for std::mt19937/mt19937_64 in C++: biski64's C code has no std::random-compatible interface (no operator(), min()/max()), so adoption is a rewrite, not a swap.
- Long-running, high-volume statistical workloads: a third party (SmokeRand author, issue #8) reports biski16/32/64 fail a Hamming-distance test at roughly 1 TiB of output, and issue #10 shows biski64 failing PractRand's expanded/extra-folding test set at 2^34 bytes (16 GB), traced to periodicity in the Weyl sequence's low bits.
- Cryptographic or adversarial contexts: not designed or claimed to be cryptographically secure.
- You want a battle-tested, widely audited generator: first published 2025, 152 stars, last commit 2025-06-12 and now stale; PCG and xoshiro have years more scrutiny and independent implementations.
- You need maximum period margin: 2^64 minimum vs 2^256 for xoshiro256++, relevant for very long single-stream runs or huge numbers of parallel streams.

## How it is fast

Each step is 3 register-sized XOR/add/rotate operations with no multiplication, no lookup tables, and no branches, which is why the author's own benchmarks show it tying wyrand/sfc64 and beating xoshiro256++/xoroshiro128++ in ns/call. A 64-bit Weyl sequence (fast_loop += 0x9999999999999999) guarantees the period never drops below 2^64 regardless of how mix/loop_mix behave, letting the design use less state than xoshiro-family generators, which need a larger state array for their period guarantee. Against std::mt19937/mt19937_64 specifically, the win is the generic 'small counter+mix generator beats tempering-heavy Mersenne Twister' gap, not a biski64-specific trick.

## Compared with alternatives

Pick biski64 over PCG (pcg-cpp), wjakob/pcg32, or xoshiro_cpp when a smaller 3-word state matters more than track record and you accept a newer, less-audited design with a 2^64 period floor. Prefer PCG or xoshiro_cpp instead when you need a C++-native, std::random-compatible API today (biski64's C code has none) or want a generator without the open statistical-weakness reports noted above.

## Integration

| | |
|---|---|
| **Form** | source-drop (C: copy struct + 3 functions from c/biski64.c) \| crate (Rust: biski64 on crates.io) |
| **Dependencies** | C: none beyond stdint.h. Rust: rand_core 0.9 (rand 0.9 / rand_xoshiro / criterion are dev-only, for the crate's own benchmark comparisons). |
| **Minimum toolchain** | C: C99 (stdint.h only, no other requirement found in source). Rust: edition 2021, no_std compatible. The C++ port used for the benchmark (planet36/prng-test-bench) needs C++20 for std::rotl, but that's the harness, not upstream biski64. |
| **Platforms** | any (plain integer ops, no SIMD/intrinsics observed); reported working on an ESP32 microcontroller in issue #11 (closed). |
| **Thread safety** | not documented; state is a plain struct/fields with no synchronization — treat each biski64_state / Biski64Rng instance as single-threaded and use biski64_stream()/from_seed_for_stream() to create separate instances for parallel use. |
| **Drop-in for the baseline** | partial — explain: same problem domain (64-bit PRNG, seedable) but not std::random-interface-compatible in C, and the Rust API is rand_core-shaped rather than a mt19937 clone; the throughput numbers come from a third-party C++ port (planet36/prng-test-bench), not the upstream C code. |

## Gotchas

- c/biski64.c ships with its own main(); PR #6 (open) proposes a fix. Until merged, strip main() or apply the workaround from that PR before including the file.
- Seeding functions run a 16-iteration warmup (biski64_warmup / the loop in from_seed_for_stream) before first use; a hand-rolled state init that skips this would start on weaker, non-warmed state.
- Two independent third-party reports found statistical weaknesses invisible to BigCrush/PractRand's default settings: SmokeRand's hamming_distr test (issue #8, \~1 TiB) and PractRand with extra folding (issue #10, fails at 2^34 bytes / 16 GB).
- Parallel-stream seeding (biski64_stream / from_seed_for_stream) needs total_streams fixed up front to space fast_loop; there is no independent jump-ahead/split function for streams created later.

## Caveats and trade-offs

The std::mt19937 comparison comes from a small third-party harness (planet36/prng-test-bench, 2 stars), not biski64's own README, whose own numbers (AMD Ryzen 9 7950X3D, vs xoshiro/PCG/wyrand/sfc64/Java) do not include std::mt19937. The harness benchmarks its own MPL-2.0 C++ port of biski64 (include/biski64.hpp, adapted from danielcota's C code), not the upstream source directly. Hardware is a generic 8-vCPU VM with no CPU model and the g++ version is unstated.

Newer, less battle-tested design than PCG/xoshiro; not cryptographically secure; guarantees only a 2^64 minimum period (smaller than xoshiro256's 2^256); author's own README benchmarks it against xoshiro/xoroshiro/PCG/wyrand/Java generators, not directly against std::mt19937.

## Maintenance

Last commit 2025-06-12, marked stale by the catalog's maintenance check; MIT-licensed and small (three functions, \~150 lines of C) so easy to vendor regardless, but two open issues (SmokeRand hamming_distr failure, PractRand extra-folding failure at 16 GB) show the statistical design is still under active scrutiny.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification B, tier now C.
- **Tier reason:** planet36/prng-test-bench is public code (prng-next-benchmark.cpp, Makefile g++ -O3 -flto=auto -march=native), but it is a 2-star personal harness, not a well-known independent suite, and no CPU model or g++ version is given. It falls short of A and does not qualify for B, so C.
- **Verifier notes:** Numbers verified in the JSON: biski64 13.80 (median) / 14.00 (mean) GB/s, std::mt19937_64 5.63/5.54, std::mt19937 5.01/5.02; the record's '13.9-14.0' and '8 threads' were slightly off. Downgraded B to C because the source is not a well-known suite. Metadata (MIT, 152 stars, last commit 2025-06-12, stale) confirmed.
- **Fields the verifier corrected:** `workload`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/danielcota/biski64>
  - <https://github.com/danielcota/biski64/blob/main/README.md>
  - <https://github.com/planet36/prng-test-bench>
  - <https://github.com/planet36/prng-test-bench/blob/main/results/prng-next-benchmark.json>
  - <https://github.com/planet36/prng-test-bench/blob/main/Makefile>
  - <https://github.com/planet36/prng-test-bench/blob/main/README.md>
  - <https://github.com/planet36/prng-test-bench/blob/main/run-benchmarks.bash>
  - <https://github.com/planet36/prng-test-bench/blob/main/include/biski64.hpp>
- **Sources the enricher read:**
  - <https://github.com/danielcota/biski64>
  - <https://github.com/danielcota/biski64/blob/main/README.md>
  - <https://github.com/danielcota/biski64/blob/main/c/biski64.c>
  - <https://github.com/danielcota/biski64/blob/main/src/lib.rs>
  - <https://github.com/danielcota/biski64/blob/main/Cargo.toml>
  - <https://github.com/danielcota/biski64/issues/8>
  - <https://github.com/danielcota/biski64/issues/10>
  - <https://github.com/danielcota/biski64/issues/1>
  - <https://github.com/danielcota/biski64/issues>
  - <https://github.com/danielcota/biski64/pulls>
  - <https://github.com/planet36/prng-test-bench/blob/main/include/biski64.hpp>
- **Raw records:** [data/wave1/verified.json](../../../data/wave1/verified.json) (id `https://github.com/danielcota/biski64`) · [data/wave1/enrich/raw/github_com_danielcota_biski64.json](../../../data/wave1/enrich/raw/github_com_danielcota_biski64.json) (enrichment confidence 0.7)

</details>
