# go-popcount (tmthrgd)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go (x86-64 POPCNT assembly, popcnt_amd64.s and popcount_amd64.s)` · `BSD-3-Clause AND MIT (portions copyright 2015 Hideaki Ohno under MIT, per the LICENSE file and the headers of popcount.go, popcount_test.go and popcnt_amd64.s)` · 🔴 abandoned

> Go amd64 POPCNT assembly that counts set bits in []byte or []uint64, 1.2-2.9x a math/bits.OnesCount64 loop.

| | |
|---|---|
| **Beats** | Go loop over math/bits.OnesCount64 (BenchmarkCountBytesGo and BenchmarkCountSlice64Go) |
| **Claimed result** | README benchmarks (refreshed 2018-01-11 in 3918361; unknown CPU, GOMAXPROCS 8, Go version unstated). CountBytes vs Go math/bits.OnesCount64 loop: 32 B 5854.04 vs 2883.25 MB/s (2.03x, derived from page data); 1K 20804.48 vs 8896.25 MB/s (2.34x, derived); 16K 28642.76 vs 9986.94 MB/s (2.87x, derived); 512M 11912.45 vs 7855.21 MB/s (1.52x, derived). CountSlice64 vs Go loop: 32 B 5804.87 vs 4840.05 MB/s (1.20x, derived); 1K 19932.68 vs 9184.79 MB/s (2.17x, derived); 16K 27414.74 vs 10012.94 MB/s (2.74x, derived); 512M 11874.91 vs 7813.19 MB/s (1.52x, derived). |
| **Workload** | population count over byte slices and []uint64 slices, 32 B to 512 MiB |
| **Metric** | throughput |
| **Hardware** | 'an AMD64 CPU with POPCOUNT support' (model not stated; GOMAXPROCS 8 from the -8 suffix) |
| **Adoption** | 25 stars, 6 forks (archived 2024-12-14) |
| **Last commit** | 2019-09-04 |
| **Links** | [repository](https://github.com/tmthrgd/go-popcount) · [benchmark](https://github.com/tmthrgd/go-popcount) |

## Verdict

The README (refreshed 2018-01-11; 'an AMD64 CPU with POPCOUNT support', GOMAXPROCS 8, Go version unstated, Travis on go1.9 that day) times the assembly against a Go loop over math/bits.OnesCount64 on the same random data. CountBytes runs 2.03x at 32 B, 2.34x at 1 KiB and 2.87x at 16 KiB, falling to 1.52x at 512 MiB (11.9 vs 7.9 GB/s); CountSlice64 runs 1.20x at 32 B, 2.74x at 16 KiB and 1.52x at 512 MiB (ratios derived from page data).

## Use it when

- Pure-Go bitmap or bitset cardinality on amd64 (Bloom filters, rank structures, similarity hashes) over cache-resident slices of 1-128 KiB, where the README shows 2.3-2.9x over the math/bits loop.
- Counting bits in a []byte directly, without converting to []uint64 yourself; CountBytes gains 2.0x even at 32 B.
- Builds that cannot raise GOAMD64 to v2, where every math/bits.OnesCount64 call keeps a POPCNT feature branch (intrinsics.go makeOnesCountAMD64).
- As a short, readable POPCNT kernel to vendor (one 95-line assembly file plus a CPUID probe).

## Skip it when

- Small []uint64 inputs: CountSlice64 gains only 1.2x at 32 B.
- Huge slices where memory bandwidth dominates: the gain falls to 1.5x at 16-512 MiB, and the asm rows themselves moved about 10% between the 2016 and 2018 README runs.
- When you need more than about one 8-byte word per cycle: the kernel is scalar POPCNT only, with no AVX2 or AVX-512 path; the sibling pospop reaches 34.8 GB/s (AVX2) and 82.1 GB/s (AVX-512) on a harder positional-count problem.
- Byte slices over 1 GiB on any path that uses countBytesGo (non-amd64 platforms, gccgo, or amd64 without POPCNT): the unsafe cast panics (see gotchas).
- Code tested with -race outside amd64, or anyone running the package's own tests with -race: countBytesGo trips checkptr (see gotchas).

## How it is fast

The kernel walks the buffer backwards 32 bytes at a time with four POPCNTQ memory-operand instructions into four separate destination registers, then sums them, so the loop body is unrolled 4x and the counts are independent. Leftover 8-byte words go through a loop that XORs its destination before POPCNT, and the final 1-7 bytes are assembled into one register with 4-, 2- and 1-byte loads so nothing is read past the end. The asm comments credit the separate registers to Intel's POPCNT false output dependency, but gc already zeroes POPCNT's destination in the baseline (golang/go commit de4edf3: MOVQ \$0 before CL 82516, an XOR after it, still present in master's amd64/ssa.go), so the measured gap is more plausibly the 4x unroll plus the per-call POPCNT feature branch the intrinsic carries unless built with GOAMD64=v2 (inference).

## Compared with alternatives

Pick it when you need a plain total popcount of a Go slice on amd64 with no cgo. pospop solves a different problem (per-bit-position counts) with SIMD kernels, and go-and and cespare/xxhash are Go-assembly siblings for bitwise ops and hashing, not counting. For C or C++ code, the verifier points to the separately catalogued libpopcnt and sse-popcount instead.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (standard library only); no go.mod in the repository, so modules resolve it as a pseudo-version |
| **Minimum toolchain** | Go 1.9 (math/bits); .travis.yml tested go1.9.x to go1.13.x; later releases not tested by the project |
| **Platforms** | amd64 assembly path (POPCNT detected at init via CPUID leaf 1 ECX bit 23); all other GOARCH values, gccgo and appengine use Go fallbacks |
| **Thread safety** | Not documented; the functions are pure (usePOPCNT is set once at package init), so concurrent calls are safe. |
| **Drop-in for the baseline** | partial — it replaces a hand-written OnesCount64 loop with one call, but it is a separate API; there is no stdlib slice popcount to substitute for |

## Gotchas

- countBytesGo (popcount_unsafe.go, used on every non-amd64 platform, under gccgo and on amd64 without POPCNT) views the input as (\*[1 &lt;&lt; 27]uint64)(unsafe.Pointer(&s[0]))[:len(s)&gt;&gt;3]. That array type caps the view at 1 GiB, so CountBytes panics with 'slice bounds out of range' for slices of 1 GiB + 8 bytes or more. The benchmarks stop at 512 MiB and the tests use small quick-check inputs, so neither reaches it (found by code reading, not executed).
- The same two-index cast fails Go's checkptr instrumentation, which -race, -msan and -asan turn on (cmd/compile base/flag.go). Only three-index slices get the special count path in ssagen/ssa.go; this two-index cast is checked as one 1 GiB object, and runtime checkptrStraddles reports 'converted pointer straddles multiple allocations' for any heap or stack slice of 8+ bytes. So `go test -race` of the package (TestCountBytesGo) and -race builds that call CountBytes off amd64 should abort (code reading, not executed).
- Harness provenance: the asm and Go README blocks were refreshed in one commit (3918361, 2018-01-11), but the Go rows carry '1k/16k/128k' labels (and one asm row '128k') while benchmark_test.go has used '1K/16K/128K' since its 2016 rewrite. The blocks were therefore pasted from separate or hand-edited runs, not one go test invocation. CPU model and Go version are not given.
- Like all Go assembly, countBytesASM is never asynchronously preempted (runtime/preempt.go excludes FuncFlagAsm), so a 512 MiB count (45 ms in the README) delays stop-the-world GC for its duration.

## Known shortcomings

- Gain only 1.5-2.9x over a math/bits loop and probably smaller on newer CPUs (POPCNT false-dependency erratum); archived. Licence BSD-3-Clause AND MIT (Hideaki Ohno portions).
- Bug found by code reading (not run): countBytesGo's (\*[1 &lt;&lt; 27]uint64)(unsafe.Pointer(&s[0]))[:len(s)&gt;&gt;3] panics for slices over 1 GiB on non-amd64, gccgo and no-POPCNT paths, and the same two-index cast fails checkptr under -race, -msan and -asan ('converted pointer straddles multiple allocations'), so go test -race of the package should abort; the numbers are unaffected (benchmarks stop at 512 MiB). Harness provenance: the README asm and Go blocks were pasted from separate or hand-edited runs ('1k' labels vs the test file's '1K'); the asm rows moved about 10% between the 2016 and 2018 runs. The Go compiler already zeroes POPCNT's destination (golang/go de4edf3), so the false-dependency rationale does not explain the gap (unroll plus a per-call feature branch more likely; inference). Assembly is never async-preempted; archived 2024-12-14.

## Caveats and trade-offs

CPU model, Go version and flags are not stated. The README numbers were refreshed on 2018-01-11, alongside the switch of the Go path to math/bits and of Travis to go1.9. The later 2018 assembly commits are formatting and generator removal, not correctness fixes. The baseline already uses the POPCNT-backed math/bits.OnesCount64 intrinsic over an unsafe []uint64 view. The 1.5-2.9x gain comes from 4x unrolling into separate destination registers, which the asm comments say is meant to dodge Intel's POPCNT false output dependency, an erratum of older Intel cores. Gc's per-call POPCNT feature check also costs the baseline time (removable with GOAMD64=v2 on Go 1.18+); this is an inference, not measured. So the gap is likely smaller on newer CPUs and compilers. At 512 MiB both sides are memory-bound (1.5x). For []uint64 input of 32 B the gain is only 1.2x. The package is derived in part from Hideaki Ohno's MIT-licensed go-popcount (Count64, hasPOPCNT, tests), though it is not a GitHub fork. amd64 only, with a CPUID check for POPCNT; other targets use the Go loop. Repository archived.

x86-64 only; requires POPCNT; pure-Go fallbacks (popcount_generic.go, safe and unsafe variants).

## Maintenance

Abandoned: last commit 2019-09-04, archived 2024-12-14 and marked 'Not maintained', no issues ever filed, 10 known importers on pkg.go.dev. The licence is BSD-3-Clause plus MIT portions from Hideaki Ohno and the code is easy to vendor, but replace the 1 GiB array cast with unsafe.Slice (Go 1.17+) first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README benchmark blocks for the POPCNT assembly against a Go loop over math/bits.OnesCount64 (code public in benchmark_test.go: BenchmarkCountBytes/CountSlice64 vs BenchmarkCountBytesGo/CountSlice64Go, same random inputs). The CPU is described only as 'an AMD64 CPU with POPCOUNT support' and no Go version or flags are given, so tier C.
- **Verifier notes:** README numbers match the record; the ratios are derived from page data, and the CountSlice64 rows were added. The licence is BSD-3-Clause plus MIT portions (both OSI, so copyable stands). Main shortcomings: no CPU model or Go version; a modest 1.5-2.9x gain over the math/bits intrinsic loop that likely shrinks on CPUs without the POPCNT false-dependency erratum; archived. Not a duplicate of any catalog entry (libpopcnt and sse-popcount are separate C/C++ entries).
- **Fields the verifier corrected:** `claimed_speedup`, `license`, `stars_or_usage`, `hardware`, `caveats`
- **Shortcomings recorded by:** verifier batch-70 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/tmthrgd/go-popcount>
  - <https://github.com/tmthrgd/go-popcount/commits>
  - <https://github.com/tmthrgd/go-popcount/commits/master/README.md>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/README.md>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/benchmark_test.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcnt_amd64.s>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount_amd64.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount_amd64.s>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount_generic.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount_safe.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount_test.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount_unsafe.go>
- **Sources the enricher read:**
  - <https://github.com/tmthrgd/go-popcount>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/README.md>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/benchmark_test.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcnt_amd64.s>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount_amd64.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount_amd64.s>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount_generic.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount_safe.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount_test.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/popcount_unsafe.go>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/.travis.yml>
  - <https://raw.githubusercontent.com/tmthrgd/go-popcount/HEAD/go.mod>
  - <https://github.com/tmthrgd/go-popcount/commits/master>
  - <https://github.com/tmthrgd/go-popcount/commit/3918361>
  - <https://github.com/tmthrgd/go-popcount/commits/master/benchmark_test.go>
  - <https://github.com/tmthrgd/go-popcount/commit/41d1db1>
  - <https://github.com/tmthrgd/go-popcount/issues?q=is%3Aissue>
  - <https://pkg.go.dev/github.com/tmthrgd/go-popcount?tab=importedby>
  - <https://github.com/golang/go/commit/de4edf3de7acda2cc7da8764ecdb3ff2e85c7a2d>
  - <https://raw.githubusercontent.com/golang/go/master/src/cmd/compile/internal/amd64/ssa.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/cmd/compile/internal/ssagen/intrinsics.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/cmd/compile/internal/ssagen/ssa.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/cmd/compile/internal/base/flag.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/runtime/checkptr.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/runtime/preempt.go>
  - https://go.googlesource.com/go/+/b99abf3cce16721d79351c92031239a27fec3d22 (WebSearch snippet only; host unreachable)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/tmthrgd/go-popcount`) · [data/wave13/enrich/raw/github_com_tmthrgd_go_popcount.json](../../../data/wave13/enrich/raw/github_com_tmthrgd_go_popcount.json) (enrichment confidence 0.8)

</details>
