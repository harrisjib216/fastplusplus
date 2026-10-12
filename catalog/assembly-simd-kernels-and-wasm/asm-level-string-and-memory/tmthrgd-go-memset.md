# go-memset (tmthrgd): Go amd64 assembly memset

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go (with amd64 assembly)` · `BSD-3-Clause` · 🔴 abandoned

> Go amd64 assembly Memset for non-zero byte fills; 8-31x a plain Go fill loop, slower than Go's zeroing loop.

| | |
|---|---|
| **Beats** | Go's own fill loop (README benchmarks BenchmarkGoSet for non-zero fill and BenchmarkGoZero for the zeroing loop idiom) |
| **Claimed result** | README benchcmp table, non-zero fill (BenchmarkSet, Go fill loop vs Memset): 2.75x at 32 B, 11.13x at 128 B, 23.84x at 1k (545 ns vs 22.9 ns), peak 31.04x at 16k, 18.54x at 128k, 13.74x at 1M, 7.92x to 8.11x at 16M-512M (-63.68% to -96.78% ns/op). Zeroing (BenchmarkZero, Go's memclr-optimised loop vs Memset): slower at small sizes (0.54x at 32 B, 0.69x at 128 B, 0.84x at 1k), parity at 16k-1M, 1.18x to 1.22x faster at 16M-512M where the AVX path switches to non-temporal stores. |
| **Workload** | memset of 32 B to 512 MB buffers; README lists Memset/GoZero/GoSet benchmark outputs and a benchcmp-style old-vs-new table. |
| **Metric** | throughput |
| **Hardware** | Not stated; benchmark names carry the -8 suffix (8 threads). |
| **Compiler and flags** | Go version and flags not stated (go test -bench; test file memset_test.go). |
| **Adoption** | 32 stars |
| **Last commit** | 2019-09-04 |
| **Links** | [repository](https://github.com/tmthrgd/go-memset) · [benchmark](https://github.com/tmthrgd/go-memset) |

## Verdict

First-party go test benchmarks in the README (CPU, Go version and flags not stated; 2016 toolchain) time Memset against a Go loop storing a variable byte: 2.75x at 32 B, 23.8x at 1 KiB (545 ns vs 22.9 ns), a peak of 31x at 16 KiB, then about 8x at 16-512 MiB (15.3 GB/s vs 1.89 GB/s). Against Go's memclr-lowered zeroing loop it is slower up to 1 KiB, equal from 16 KiB to 1 MiB and 1.18-1.22x faster at 16-512 MiB thanks to non-temporal stores.

## Use it when

- Pure-Go code on amd64 that fills large byte buffers with a non-zero value (0xFF masks, padding bytes, test patterns), where the README shows 11-31x over the Go loop between 128 B and 128 KiB.
- Fills of 16 MiB and more that will not be read back soon, where the non-temporal path gave 1.18-1.22x even over Go's memclr loop in the 2016 measurements.
- Code that must avoid cgo: a C memset reached through cgo pays the cgo call cost on every call, while this is a plain Go assembly call.
- As a reference for a small, readable SSE/AVX fill kernel to vendor and adapt (about 100 lines of Go assembly, BSD-3-Clause).

## Skip it when

- Zeroing: use the `for i := range b { b[i] = 0 }` idiom or clear(b); the README shows Memset at 0.54x, 0.69x and 0.84x of it at 32 B, 128 B and 1 KiB, and parity from 16 KiB to 1 MiB.
- CPUs without SSE4.1 (for example AMD K8/K10 and 65 nm Core 2): any call with 16 or more bytes executes PINSRB and dies with SIGILL (see gotchas).
- Buffers that are filled and then read right away at 16 MiB and above: the non-temporal stores push the data out of cache, so the consumer pays DRAM latency.
- Latency-sensitive services with very large fills: one call over hundreds of MiB runs as an unpreemptible assembly loop (35 ms at 512 MiB in the README).
- Projects that want a maintained dependency: archived on 2024-12-14, no go.mod, CI last ran go1.10-go1.13 on Travis.

## How it is fast

The byte is broadcast into an XMM register (PINSRB then PSHUFB with a zero shuffle mask) and the buffer is written backwards from its end: 16-byte MOVOU stores without AVX, or two 32-byte VMOVDQU stores per iteration when AVX is present and the length is at least 64 bytes, with a byte loop for the last 1-15 bytes. From 16 MiB up it aligns the end to 32 bytes and switches to four VMOVNTDQ non-temporal stores per 128-byte iteration followed by SFENCE, which avoids reading destination lines into cache. The portable fallback uses the copy-doubling idiom (write one byte, then copy(data[i:], data[:i]) with i doubling), which rides on runtime memmove.

## Compared with alternatives

Pick it over fancy-memset or nadavrot/memset_benchmark when the caller is Go and cgo is off the table, because those are C/assembly memsets measured against glibc. The riteme memset-by-memcpy-doubling gist uses the same idea as this package's portable fallback and needs no assembly, which makes it the safer choice if you cannot vouch for SSE4.1 on every target.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/sys/cpu (amd64 build only, for the AVX check); the repository has no go.mod, so Go modules resolve it as a pseudo-version |
| **Minimum toolchain** | go1.10 per the 2018 'Update assembly to go1.10' commit (VINSERTF128 mnemonic); .travis.yml tested go1.10.x to go1.13.x; newer Go releases not tested by the project |
| **Platforms** | amd64 assembly path (needs SSE4.1 for lengths of 16 bytes or more; AVX optional and detected); every other GOARCH, gccgo and appengine use the pure-Go copy-doubling fallback |
| **Thread safety** | Not documented; the function keeps no mutable state (useAVX is read-only after init), so concurrent calls on disjoint slices are safe; overlapping writers race as with any fill. |
| **Drop-in for the baseline** | partial — it replaces a hand-written fill loop with one call, but it is a new API, not a compiler-recognised idiom, and for value 0 it is slower than the loop the compiler already lowers to memclr |

## Gotchas

- Unchecked SSE4.1 requirement: memset_amd64.s executes PINSRB (an SSE4.1 instruction, CPUID.01H:ECX bit 19) and PSHUFB (SSSE3) for every length of 16 bytes or more, but only AVX is detected (cpu.X86.HasAVX). Go's amd64 baseline only guarantees SSE2, so the package can SIGILL on x86-64 CPUs that Go itself supports. The verifier's note named SSSE3; the actual floor is SSE4.1.
- The published numbers are old: README output dates from 2016-11-11 (Go 1.7-era toolchain, CPU not named, GOMAXPROCS 8). The 2018 commits only replaced a hand-encoded VINSERTF128 with its mnemonic, rewrote two constants and moved CPU detection to x/sys/cpu, so the loops benchmarked are the ones shipped. Today's runtime memclr_amd64.s uses REP STOSQ from 2 KiB on ERMS CPUs and VMOVNTDQ from 32 MiB on AVX2 CPUs, so the 1.18-1.22x zeroing gain at 128-512 MiB probably no longer holds (inference, not measured).
- The non-zero baseline is the slowest possible Go version (a byte loop at about 1.9 GB/s at every size). The package's own fallback, the copy-doubling idiom, was never benchmarked against Memset, so the gain over the best pure-Go fill is unknown and certainly far below 8-31x for large buffers. README labels ('1k') do not match the committed test file ('1K') from the same commit, and the benchcmp rows were renamed by hand to pair GoZero/GoSet with Memset.
- Go never asynchronously preempts assembly functions (runtime/preempt.go skips FuncFlagAsm code), so a stop-the-world GC waits for the whole call; split fills of hundreds of MiB into chunks if pause latency matters.

## Known shortcomings

- Baseline is a plain Go loop, not libc; slower than Go's own zeroing loop under 16 KB; README numbers date from 2016-11, before the 2018 assembly rewrite; SSSE3 is not checked at runtime. Repo archived 2024-12-14.
- Unchecked SSE4.1 requirement: memset_amd64.s runs PINSRB (SSE4.1) and PSHUFB on every call of 16 bytes or more but only AVX is detected, so it SIGILLs on CPUs without SSE4.1 (the earlier SSSE3 note understated the floor). The baseline is a byte loop (about 1.9 GB/s) and the package's own copy-doubling fallback was never benchmarked against it; the 2018 commits were cosmetic, so the shipped loops are the ones in the 2016 numbers; current Go memclr uses REP STOSQ from 2 KiB and VMOVNTDQ from 32 MiB, so the 1.18-1.22x zeroing gain at 128-512 MiB is probably gone (inference). Assembly is never async-preempted (35-45 ms GC stall at 512 MiB); archived 2024-12-14, no go.mod.

## Caveats and trade-offs

Baseline is a plain Go loop, not libc memset; for zeroing the Go compiler already lowers the loop to runtime memclr, and Memset is slower than it below 16k. The README benchmark output was last updated on 2016-11-11 (README commit history), before the April 2018 commits that rewrote the assembly for go1.10 and moved CPU detection to x/sys/cpu, so the published numbers were measured on an older version of the code with a 2016 Go toolchain (sub-benchmarks imply Go 1.7+); no Go version, CPU model or flags are given (the -8 suffix is GOMAXPROCS=8). The amd64 assembly uses PSHUFB (SSSE3) for buffers of 16 bytes or more without checking for SSSE3; only AVX is detected. Large fills (16 MB and up) use VMOVNTDQ non-temporal stores, which bypass cache and can hurt a consumer that reads the buffer right after. The repository was archived by its owner on 2024-12-14 and the description says 'Not maintained'. Later Go toolchains may behave differently.

Go package with a pure-Go fallback (memset_other.go); only the amd64 build uses assembly. Archived read-only by the owner on 2024-12-14 and marked 'Not maintained' in the README.

## Maintenance

Abandoned: last commit 2019-09-04, archived 2024-12-14 and marked 'Not maintained', no issues ever filed and 3 known importers on pkg.go.dev. It is BSD-3-Clause and small enough to vendor, but add an SSE4.1 check before you rely on it.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party go test benchmarks (memset_test.go: BenchmarkMemset vs BenchmarkGoSet/BenchmarkGoZero) with README output and a benchcmp table, but no Go version, flags or CPU model, so not A; no independent measurement, so C.
- **Verifier notes:** README numbers and old/new column assignment check out (old = BenchmarkGoSet/GoZero, new = BenchmarkMemset); README even prints its own speedup column. Repo archived 2024-12-14, last commit 2019-09-04, BSD-3-Clause (Modified BSD LICENSE), 32 stars. Shortcomings: Go-loop baseline not libc, slower than Go's zeroing loop under 16k, numbers predate the 2018 assembly rewrite, no CPU or Go version, unchecked SSSE3.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-63 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/tmthrgd/go-memset>
  - <https://github.com/tmthrgd/go-memset/commits>
  - <https://github.com/tmthrgd/go-memset/commits/master/README.md>
  - <https://raw.githubusercontent.com/tmthrgd/go-memset/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/tmthrgd/go-memset>
  - <https://raw.githubusercontent.com/tmthrgd/go-memset/HEAD/README.md>
  - <https://raw.githubusercontent.com/tmthrgd/go-memset/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tmthrgd/go-memset/HEAD/memset_amd64.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-memset/HEAD/memset_amd64.s>
  - <https://raw.githubusercontent.com/tmthrgd/go-memset/HEAD/memset_other.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-memset/HEAD/memset_test.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-memset/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/tmthrgd/go-memset/HEAD/go.mod>
  - <https://github.com/tmthrgd/go-memset/commits/master>
  - <https://github.com/tmthrgd/go-memset/commit/ee9bc4d>
  - <https://github.com/tmthrgd/go-memset/commit/bc1da5c>
  - <https://github.com/tmthrgd/go-memset/commits/master/memset_test.go>
  - <https://github.com/tmthrgd/go-memset/commits/master/README.md>
  - <https://github.com/tmthrgd/go-memset/issues?q=is%3Aissue>
  - <https://pkg.go.dev/github.com/tmthrgd/go-memset?tab=importedby>
  - <https://raw.githubusercontent.com/golang/go/master/src/runtime/memclr_amd64.s>
  - <https://raw.githubusercontent.com/golang/go/master/src/cmd/compile/internal/walk/range.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/runtime/preempt.go>
  - https://felixcloutier.com/x86/pinsrb:pinsrd:pinsrq (WebSearch snippet only)
  - https://code.google.com/p/go/issues/detail?id=5373 (WebSearch snippet only)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/tmthrgd/go-memset`) · [data/wave13/enrich/raw/github_com_tmthrgd_go_memset.json](../../../data/wave13/enrich/raw/github_com_tmthrgd_go_memset.json) (enrichment confidence 0.8)

</details>
