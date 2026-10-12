# UMASH

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Crypto and hashing](../README.md) › [Non-cryptographic hashes](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🟢 active

> Keyed CLMUL-based C string hash with a proven almost-universal collision bound; 1.5-2.5x CityHash64 bulk throughput, roughly xxh3 parity.

| | |
|---|---|
| **Beats** | CityHash64 (City64); xxHash xxh3 at rough parity only |
| **Claimed result** | SMHasher README rows: umash64 26628.37 MiB/s vs xxh3 20853.74 MiB/s (+28%, derived from page data). That gap is inflated because the linked logs convert umash at 3600 MHz and xxh3 at '3 ghz'. In bytes/cycle it is 7.756 vs 7.289, about +6% (derived from page data). The sortable Ryzen 5 3350G table has umash64 at 21963.54 vs xxh3 20853.74 MiB/s, about +5% (derived). On the same suite's EPYC 9554P and i7-6820HQ tables umash64 is slower than xxh3 (40087.20 vs 45761.99 and 30586.04 vs 44601.42 MiB/s). It is also slower on small keys (39.87 vs 29.46 cycles/hash). It clearly beats City64 on bulk throughput: about 1.5x on the 3350G table, 2.5x on EPYC 9554P and 1.9x on i7-6820HQ (derived from page data). |
| **Workload** | SMHasher bulk-hash speed test, 262144-byte keys, run for many hash functions on the same machine/build in rurban/smhasher. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 5 3350G 3.6GHz (SMHasher default table); also the SMHasher AMD EPYC 9554P and Intel i7-6820HQ tables; the author's own numbers are on an AMD EPYC 7713 and Apple M1 performance cores |
| **Compiler and flags** | rurban/smhasher CMakeLists.txt: Release build type by default with -march=native; the page does not state the compiler name or version. UMASH's own README separately cites 10.9 byte/cycle (39.5 GiB/s) on an AMD EPYC 7713 and requires a gcc-compatible compiler. |
| **Adoption** | 162 stars |
| **Last commit** | 2026-01-11 |
| **Links** | [repository](https://github.com/backtrace-labs/umash) · [benchmark](https://github.com/rurban/smhasher/blob/master/README.md) |

## Verdict

In rurban/smhasher's 256 KiB bulk test (CMake Release, -march=native, compiler unstated), umash64 did 21,964 MiB/s vs City64 14,390 on a Ryzen 5 3350G (about 1.5x), 40,087 vs 15,791 on an EPYC 9554P (2.5x) and 30,586 vs 16,062 on an i7-6820HQ (1.9x). Against xxh3 it is +5% on the 3350G and 12% and 31% slower on the other two. The README's headline 26,628 vs 20,854 MiB/s row compares runs converted at different clock rates, so it overstates the gap.

## Use it when

- Hash tables, sharding or sampling keyed with random per-process params, where you want a stated worst-case collision bound (below ceil(s/4096)\*2^-55 for inputs of s bytes or fewer) instead of an empirical SMHasher pass
- Content fingerprinting or dedup that needs 128-bit fingerprints with a collision bound below 2^-70 for inputs up to 5 GiB, made reproducible across runs with umash_params_derive and a per-program secret
- Replacing CityHash64 in C on x86-64 with CLMUL or aarch64 with the crypto extension: 1.5-2.5x its bulk throughput in rurban SMHasher and slightly fewer cycles per small key
- Streaming or chunked inputs: the sink API gives the same value as a one-shot hash, and a sink can be byte-copied to snapshot its state
- Long buffers (1 KiB and up) on CPUs that report VPCLMULQDQ, where the AVX2 path gives the README's 10.9 bytes/cycle (39.5 GiB/s) on an EPYC 7713

## Skip it when

- Latency-bound small keys: rurban SMHasher shows about 41 cycles per 1-31 byte key against about 29 for xxh3 and wyhash and 22 for rapidhash on the Ryzen 5 3350G table
- When you only want the most bulk throughput: it trails xxh3 by 12% on EPYC 9554P and 31% on i7-6820HQ, and the AES-based gxhash and lanehash rows are more than 2x faster
- MSVC, big-endian, 32-bit targets, or CPUs without CLMUL/PMULL: umash.c stops with #error on an unsupported platform, and the README says only gcc-compatible compilers work
- Adversaries who can learn or infer the params: the header says the bounds then no longer apply. It is not a MAC or PRF, and umash_params_derive with a NULL key uses the public default secret 'Do not use UMASH VS adversaries.'
- Hash values persisted across library versions when params come from umash_params_prepare: the README says the ABI is not final and the same random bytes may produce different params later

## How it is fast

It follows the UMAC/VHASH two-level design. 256-byte blocks are compressed by an 'OH' function that is mostly PH, a carry-less analogue of NH (XOR each 16-byte chunk with key words, then one PCLMULQDQ/PMULL per chunk). The last chunk goes through ENH, a 64x64-&gt;128 integer multiply. Block outputs feed a Horner polynomial hash modulo 2^61-1 with lazy reduction. Inputs of 8 bytes or less take a SplitMix64-style mixer, and inputs of 9-16 bytes take a single ENH multiply. From 1 KiB up, umash_long.inc switches to an AVX2 + VPCLMULQDQ routine picked at runtime through CPUID.

## Compared with alternatives

Pick UMASH over xxHash (xxh3), wyhash and rapidhash when a provable almost-universal bound or a 128-bit fingerprint with a stated collision probability matters more than small-key latency. Against CLHash, the other CLMUL almost-universal hash in the catalog, UMASH's case rests on its aarch64 PMULL port, incremental API and fingerprint mode.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none (Salsa20 for umash_params_derive is built in; systemtap sdt.h only if UMASH_STAP_PROBE is set) |
| **Minimum toolchain** | gcc-compatible C compiler with GCC 5-era integer-overflow builtins and __uint128_t; C11 &lt;stdatomic.h&gt; for x86-64 dynamic dispatch; inline asm used on GCC 6+ / clang 10+ (optional). MSVC not supported |
| **Platforms** | x86-64 with CLMUL (-mpclmul), plus a runtime-dispatched AVX2+VPCLMULQDQ path for inputs of 1 KiB or more; little-endian aarch64 with crypto extension (-march=armv8-a+crypto) |
| **Thread safety** | One-shot umash_full/umash_fprint only read a caller-owned const umash_params, and the lazily set dispatch pointer is a C11 atomic. Sharing a umash_state across threads is not documented; treat each state as single-owner. |
| **Drop-in for the baseline** | no |

## Gotchas

- The seed argument changes the output but carries no collision bound. Only randomly generated, secret umash_params give the guarantee.
- umash_full(..., which=1) computes a full fingerprint and returns its second half, so it is as slow as umash_fprint.
- The proof has a known gap. Open issue #40 (Sept 2026) shows the whitepaper's 'reduce mod 2^61-1 loses \~6 bits' step does not follow as written. Third-party paper proofs, only partly Lean-checked, restore the headline 64-bit and 128-bit bounds in an ideal full-key model that does not cover Salsa20-derived params. The maintainer acknowledged this and a doc update is pending.
- The Python reference (umash_reference.py) uses one polynomial multiplier for both fingerprint halves, and issue #40 shows its fingerprint does not meet the 2^-83 bound. The C library uses two independent multipliers and is not affected.

## Known shortcomings

- The 28% win over xxh3 is a clock artifact (UMASH row at 3600 MHz, xxh3 row at '3 GHz'): \~6% by bytes/cycle and \~5% in the sortable Ryzen 3350G table, and it is slower than xxh3 on EPYC 9554P and an i7. Real margin is over CityHash64 (1.5-2.5x). Needs CLMUL.
- Requires CLMUL/PMULL; GCC-compatible compilers only (no MSVC); ABI not final. Small keys \~41 vs xxh3 \~29 cycles. Issue #40 (Sep 2026) reports a gap in the whitepaper's collision-bound proof (third-party proofs restore it in an ideal-key model); the Python reference fingerprint fails the bound. Low activity since 2022.

## Caveats and trade-offs

UMASH's own README says its throughput is only 'comparable to' XXH3, HalftimeHash and MeowHash. In the independent SMHasher data it is roughly at parity with xxh3: about +5-6% on the Ryzen 3350G once clocks are normalized, and 12-31% slower on EPYC 9554P and i7-6820HQ. It is also slower than xxh3 on 1-31 byte keys. The README's +28% gap comes from runs converted at different clock assumptions. The clear win is over older incumbents such as CityHash64. Its distinguishing feature is an almost-universal collision bound. The README says the function is frozen but the implementation and ABI are not finalized.

Requires x86-64 CLMUL or aarch64 PMULL crypto extension; provides a proven almost-universal collision bound unlike most fast non-crypto hashes, but the ABI around umash_params_prepare is explicitly not yet finalized.

## Maintenance

Active but low-churn: the algorithm has been frozen since 2022 and 2025-2026 commits are warning fixes, formatting and test-dependency updates (last 2026-01-11). It is MIT-licensed and small enough to vendor (two C files plus an optional .inc), and a thin Rust wrapper, umash-rs, exists (2 stars, last push 2025-01).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): downgrade; tier before verification B, tier now B.
- **Tier reason:** rurban/smhasher is a well-known independent suite with public code (CMakeLists.txt: CMake Release default plus -march=native) and named CPUs, but it never states the compiler, and the umash64 and xxh3 README rows come from different runs, so it is not A. It shows a consistent win over City64 on all three machines but only parity with xxh3.
- **Verifier notes:** Last commit is 2026-01-11 and the README says the implementation isn't finished, so status is 'active' rather than 'finished'. The license is MIT, and the stars (162) and last_commit are correct. A 'not-faster' reject against xxh3 alone is arguable, but the entry is kept by re-basing it on CityHash64, which is in the known list.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `hardware`, `maintenance_status`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/rurban/smhasher/blob/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/umash64.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/xxh3.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/City64.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/table.html>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/epyc.html>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/i7.html>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/CMakeLists.txt>
  - <https://github.com/backtrace-labs/umash>
  - <https://raw.githubusercontent.com/backtrace-labs/umash/master/README.md>
- **Sources the enricher read:**
  - <https://github.com/backtrace-labs/umash>
  - <https://raw.githubusercontent.com/backtrace-labs/umash/master/README.md>
  - <https://github.com/backtrace-labs/umash/blob/master/umash.h>
  - <https://github.com/backtrace-labs/umash/blob/master/umash.c>
  - <https://github.com/backtrace-labs/umash/blob/master/umash_long.inc>
  - <https://github.com/backtrace-labs/umash/issues>
  - <https://github.com/backtrace-labs/umash/pulls>
  - <https://github.com/backtrace-labs/umash/commits/master>
  - <https://github.com/backtrace-labs/umash/issues/40>
  - <https://github.com/backtrace-labs/umash-rs>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/README.md>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/umash64.txt>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/table.html>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/epyc.html>
  - <https://raw.githubusercontent.com/rurban/smhasher/master/doc/i7.html>
- **Raw records:** [data/wave7/verified.json](../../../data/wave7/verified.json) (id `https://github.com/backtrace-labs/umash`) · [data/wave7/enrich/raw/github_com_backtrace_labs_umash.json](../../../data/wave7/enrich/raw/github_com_backtrace_labs_umash.json) (enrichment confidence 0.62)

</details>
