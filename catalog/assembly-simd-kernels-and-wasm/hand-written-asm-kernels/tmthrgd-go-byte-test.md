# go-byte-test (tmthrgd)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go (x86-64 SSE assembly, test_amd64.s)` · `BSD-3-Clause` · 🔴 abandoned

> SSE assembly predicate for Go that checks whether every byte of a slice equals one value; 5-42x a naive Go loop.

| | |
|---|---|
| **Beats** | Go gc compiler output for the loop that checks every byte equals a value (BenchmarkGoTest) |
| **Claimed result** | README speedup table (committed 2017-02-23 in 2eb5216; unknown CPU, GOMAXPROCS 8, Go version unstated), naive Go byte loop to go-byte-test: 32 B 893.80 to 4488.67 MB/s (5.02x), 128 B 15.45x, 1K 1177.11 to 40050.28 MB/s (34.02x), 16K 42.28x, 128K 36.34x, 1M 24.66x, 16M 14.67x, 128M 14.71x, 512M 1172.27 to 17316.31 MB/s (14.77x). |
| **Workload** | test whether every byte of a slice equals a given value, sizes 32 B to 512 MiB |
| **Metric** | throughput |
| **Hardware** | not stated (GOMAXPROCS 8 from the -8 suffix) |
| **Adoption** | 1 star, 0 forks (archived 2024-12-14) |
| **Last commit** | 2019-09-04 |
| **Links** | [repository](https://github.com/tmthrgd/go-byte-test) · [benchmark](https://github.com/tmthrgd/go-byte-test) |

## Verdict

The README (benchmark table committed 2017-02-23 in 2eb5216, unknown CPU, GOMAXPROCS 8, Go version unstated) compares BenchmarkTest against BenchmarkGoTest, a naive range loop compiled by gc, on all-equal buffers: 5.02x at 32 B, 34.02x at 1 KiB, 42.28x at 16 KiB, and about 14.7x (17.3 vs 1.17 GB/s) from 16 MiB to 512 MiB where both are bound by memory and the scalar loop respectively. The assembly measured then is the code shipped now: later commits only replaced hand-encoded PTEST bytes with the mnemonic (48837c9, byte-identical encoding) and dropped the generator (de2b86e, whitespace-only change to test_amd64.s).

## Use it when

- Hot checks that a buffer is all-zero or all one fill byte (sparse-block detection, zero-page skipping, verifying a memset or wiped key) on amd64 with the gc toolchain.
- Buffers from about 128 B to a few hundred KiB, where the README shows 15-42x over a naive Go loop (16 KiB: 325 ns vs 13760 ns).
- Large buffers where you want to run at memory bandwidth instead of about 1.2 GB/s: from 16 MiB up the README shows about 17 GB/s, roughly 14.7x the naive loop.
- Code that wants an early exit on the first mismatch, which a bytes.Count-based check does not give.

## Skip it when

- Inputs under 16 bytes: they go straight to a byte loop in assembly plus a non-inlinable call, so expect no gain; 32 B is only 5x.
- Any non-amd64 target (arm64, ppc64le, wasm) or gccgo: you get the same scalar loop you would write yourself.
- Fleets that may include amd64 CPUs without SSE4.1 (pre-Penryn Intel, AMD K8/K10): there is no CPUID check, so PINSRB/PTEST raise SIGILL instead of falling back.
- Projects that need a maintained dependency: the repo is archived (2024-12-14), described as not maintained, has no go.mod, 1 star and one known importer (tmthrgd/go-bitset).
- When you already depend on a newer SIMD library: the kernel is 128-bit SSE only, with no AVX2 or AVX-512 path, so it leaves L1/L2 throughput on the table on current CPUs.

## How it is fast

The value is broadcast to all 16 lanes of an XMM register (PINSRB then PSHUFB with a zero mask); the routine then walks the slice backwards from the end in 128-byte blocks (eight unaligned MOVOU loads), XORs each 16-byte vector with the broadcast, ORs the eight results together and does a single PTEST per block, exiting on the first non-zero. Remainders drop to 64-byte and 16-byte vector blocks and finally a byte loop, so there is no over-read past the slice and no alignment prologue. This is plain SIMD compare-and-reduce with one branch per 128 bytes; the gain comes from Go's gc compiler never auto-vectorizing the scalar loop.

## Compared with alternatives

Pick it over hexon/vectorcmp when you need only a yes/no all-equal answer with early exit and no output bitmask; vectorcmp's VectorEquals8 is AVX2, maintained and re-measured in 2025, so prefer it when you need per-element results or a supported dependency. Compared with bwesterb/go-and (AVX2 bitwise ops on byte slices), this solves a different predicate but has the same naive-Go-loop style baseline.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at run time; tests import github.com/tmthrgd/go-memset |
| **Minimum toolchain** | Go gc toolchain 1.10+ (the PTEST mnemonic replaced hand-encoded bytes in 48837c9, 'Update assembly for go1.10'); Travis tested 1.10-1.13; no go.mod, so it is imported as a pseudo-version |
| **Platforms** | amd64 with SSE4.1 (SSSE3 PSHUFB, SSE4.1 PINSRB and PTEST) for the fast path; any Go target via the scalar fallback |
| **Thread safety** | Pure function over a read-only slice with no shared state; safe for concurrent use (not stated in the docs, follows from the code). |
| **Drop-in for the baseline** | partial - same semantics as the hand-written range loop it replaces, but the call is a new package function rather than a stdlib API |

## Gotchas

- No runtime CPU feature check: testAsm uses PSHUFB (SSSE3) and PINSRB/PTEST (SSE4.1) unconditionally, while Go's amd64 baseline (GOAMD64=v1) only guarantees SSE2. The Go stdlib's own bytealg.Count checks internal/cpu for POPCNT/AVX2 and broadcasts with SSE2 PUNPCKLBW/PSHUFL; an SSE2-only PCMPEQB/PMOVMSKB version would have avoided the requirement.
- The benchmark only measures the full-scan case: both BenchmarkTest and BenchmarkGoTest fill the buffer entirely with the value, so early-exit behaviour and mismatch latency are never timed. TestCorrect's negative case only flips the last byte, which is the first block the backward scan reads, so mismatches deep in the buffer are covered by code reading, not tests (the code reviewed this session handles them correctly).
- The baseline is the naive byte loop written inline in the benchmark; a uint64-word Go loop or the SIMD-backed stdlib route bytes.Count(data, []byte{value}) == len(data) (internal/bytealg count_amd64.s, SSE/AVX2 + POPCNT, no early exit) were not measured and would narrow the gap.
- The function writes R15 in the byte-tail loop; Go's assembler treats R15 as clobbered by global accesses under -dynlink (plugins, shared builds). The routine touches no globals, so it assembles, but it is a register a modern rewrite would avoid.

## Known shortcomings

- Naive byte-loop baseline only; no SSE4.1/SSSE3 CPUID check; archived, 1 star.
- Assembly read: no bug, the backward scan is correct with no over-read. No CPUID check (PSHUFB, PINSRB and PTEST need SSE4.1, so SIGILL on older amd64 CPUs that Go supports); the benchmark times only the all-equal full-scan case; TestCorrect only flips the last byte; the SIMD stdlib route bytes.Count was never compared; one known importer (go-bitset). The README numbers are for code still shipped (48837c9 is byte-identical PTEST, de2b86e whitespace only).

## Caveats and trade-offs

No CPU model, Go version or flags; only GOMAXPROCS 8 can be read from the -8 suffix. The README table was committed on 2017-02-23. The assembly was touched on 2018-04-22 only to replace hand-encoded PTEST bytes with the mnemonic (48837c9) and to drop the tmthrgd/asm generator; neither is a correctness fix. The baseline is a naive byte-at-a-time range loop written inline in the benchmark. A uint64-wise Go loop, or a stdlib SIMD route such as bytes.Count(data, []byte{value}) == len(data) through internal/bytealg, was not compared and would narrow the gap. The 34-42x peaks are at L1/L2-resident sizes; from 16M up it is memory-bound at about 17 GB/s (14.7x). The benchmark data is all equal to the value, so it measures the full-scan case only. The assembly uses PSHUFB (SSSE3) and PINSRB/PTEST (SSE4.1) with no CPUID check: amd64 CPUs without SSE4.1 (pre-Penryn Intel, AMD K10) will fault. It also uses R15, which Go's assembler reserves under -dynlink. amd64 only; other targets get the plain Go loop. Repository archived, 1 star, 12 commits.

x86-64 assembly only, generic fallback elsewhere; README describes it as SSE accelerated (128-bit vectors, no AVX2).

## Maintenance

Archived 2024-12-14 and marked not maintained (last commit 2019-09-04, 12 commits, no issues ever filed), but BSD-3-Clause and a 126-line assembly file small enough to vendor; add an SSE4.1 CPUID guard (golang.org/x/sys/cpu) before shipping it to unknown hardware.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables comparing BenchmarkTest with BenchmarkGoTest (code public in test_test.go, same sizes and memset setup), with the README's own speedup column. No CPU model, Go version or flags are given, so tier C.
- **Verifier notes:** README numbers match the record exactly (16M is 14.67x, 128K 36.34x, both added). Main shortcomings: no hardware or Go version; a naive byte-loop baseline only; no runtime SSE4.1 check; archived and practically unused (1 star). Not a duplicate; go-memset and go-hex are separate tmthrgd entries.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-70 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/tmthrgd/go-byte-test>
  - <https://github.com/tmthrgd/go-byte-test/commits>
  - <https://github.com/tmthrgd/go-byte-test/commits/master/README.md>
  - <https://github.com/tmthrgd/go-byte-test/commits/master/test_amd64.s>
  - <https://github.com/tmthrgd/go-byte-test/commit/48837c9>
  - <https://raw.githubusercontent.com/tmthrgd/go-byte-test/HEAD/README.md>
  - <https://raw.githubusercontent.com/tmthrgd/go-byte-test/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tmthrgd/go-byte-test/HEAD/test_amd64.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-byte-test/HEAD/test_amd64.s>
  - <https://raw.githubusercontent.com/tmthrgd/go-byte-test/HEAD/test_other.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-byte-test/HEAD/test_test.go>
- **Sources the enricher read:**
  - <https://github.com/tmthrgd/go-byte-test>
  - <https://github.com/tmthrgd/go-byte-test/commits/master>
  - <https://github.com/tmthrgd/go-byte-test/commit/2eb5216>
  - <https://github.com/tmthrgd/go-byte-test/commit/de2b86e>
  - <https://github.com/tmthrgd/go-byte-test/commit/48837c9>
  - <https://github.com/tmthrgd/go-byte-test/issues?q=is%3Aissue>
  - <https://raw.githubusercontent.com/tmthrgd/go-byte-test/HEAD/README.md>
  - <https://raw.githubusercontent.com/tmthrgd/go-byte-test/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tmthrgd/go-byte-test/HEAD/test_amd64.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-byte-test/HEAD/test_amd64.s>
  - <https://raw.githubusercontent.com/tmthrgd/go-byte-test/HEAD/test_other.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-byte-test/HEAD/test_test.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-byte-test/HEAD/.travis.yml>
  - <https://pkg.go.dev/github.com/tmthrgd/go-byte-test?tab=importedby>
  - <https://raw.githubusercontent.com/golang/go/master/src/internal/bytealg/count_amd64.s>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/tmthrgd/go-byte-test`) · [data/wave13/enrich/raw/github_com_tmthrgd_go_byte_test.json](../../../data/wave13/enrich/raw/github_com_tmthrgd_go_byte_test.json) (enrichment confidence 0.7)

</details>
