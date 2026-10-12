# fastxor (lukechampine)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go (AVX/SSE assembly, xor_amd64.s)` · `MIT` · 🔴 abandoned

> Go package that xors byte slices with AVX2/SSE2 assembly; about 5x a word-wise Go loop, 40x a byte loop.

| | |
|---|---|
| **Beats** | naive byte-wise Go for loop and a word-wise (uint64) Go loop, compiled by the Go gc compiler |
| **Claimed result** | README BenchmarkBytes table (committed 2018-07-06 in 000cb37; unknown AVX2-capable CPU, GOMAXPROCS 4, Go version unstated): AVX 65k 67217.99 MB/s vs byte-wise loop 1684.45 MB/s (39.9x, derived from page data) and word-wise loop 13203.25 MB/s (5.09x, derived); 1024 B AVX 66089.39 vs byte-wise 1677.18 (39.4x) and word-wise 11455.33 MB/s (5.77x); 16 B AVX 2579.65 vs byte-wise 1263.77 (2.04x) and word-wise 2170.17 MB/s (1.19x); SSE 65k 32619.21 MB/s (2.47x over word-wise). README conclusion: '2-40 times faster than a naive for loop'. The README's 'about 6 times faster' Block claim is struck as cross-run: it divides a Block run from 2018-10-11 (1.18 ns, commit ab5bbce) by a Bytes/16 run from 2018-07-06 (6.20 ns); in the 2018-07-06 run itself Block took 2.72 ns, a 2.3x gain (derived from page data). |
| **Workload** | xor of byte slices of 16 B, 1024 B and 65536 B, run in place on one zeroed buffer (Bytes(buf, buf, buf)) with SetBytes counting one stream; plus a specialised 16-byte Block function |
| **Metric** | throughput |
| **Hardware** | not stated (the AVX2 path ran, so an AVX2-capable x86-64 CPU; GOMAXPROCS 4 from the -4 suffix) |
| **Adoption** | 76 stars, 4 forks |
| **Last commit** | 2021-03-22 |
| **Links** | [repository](https://github.com/lukechampine/fastxor) · [benchmark](https://github.com/lukechampine/fastxor) |

## Verdict

The README's go test benchmark ran in 2018 on an unnamed AVX2 x86-64 machine (GOMAXPROCS 4, Go version unstated). It xors one aliased, zeroed buffer in place. At 64 KiB, AVX2 ran at 67.2 GB/s against 13.2 GB/s for a word-wise Go loop (5.1x) and 1.7 GB/s for a byte loop that still had bounds checks (39.9x). At 16 bytes the gains fall to 1.19x and 2.04x. Go's crypto/subtle.XORBytes was not measured. fastxor's own SSE2 row (32.6 GB/s at 64 KiB) is the closest stand-in and implies about 2x for AVX2.

## Use it when

- amd64 machines with AVX2 that xor cache-resident buffers of roughly 256 B to 64 KiB (keystream application, one-time pads, RAID-style parity), where about 2x over an SSE2 loop matters.
- Code pinned to a Go toolchain older than 1.20, which has no exported crypto/subtle.XORBytes, that wants something faster than a hand-written loop.
- Hot loops that xor exactly 16-byte blocks on amd64 (CBC/CTR-style block-cipher glue): Block inlines to two 64-bit xors with no call overhead.
- As a small, readable MIT-licensed Go-assembly xor kernel to vendor and adapt (about 190 lines of assembly).

## Skip it when

- Go 1.20+ code by default: crypto/subtle.XORBytes is in the standard library. It has SSE2 assembly on amd64, a 64-byte NEON loop on arm64 and assembly for ppc64, panics on a short dst and rejects partial overlap. fastxor's AVX2 gain over it was never measured; inferred from fastxor's own SSE2 row, it is about 2x, and only at cache-resident sizes.
- arm64 (Apple silicon, Graviton), riscv64, wasm and other non-x86 targets: fastxor falls back to a byte-wise Go loop there, slower than the standard library's NEON path.
- Slices under about 64 bytes: the assembly call cannot be inlined and its cost dominates. The README's own 16-byte row is only 1.19x a word-wise Go loop, and issue #4 (Core i5, Go 1.16) reports no gain over an inlined word loop on 64-byte blocks.
- Buffers far larger than cache: the benchmark stops at 64 KiB in cache, and at DRAM bandwidth vector width barely matters.
- Projects that need upkeep: 12 commits, last change 2021-03-22, no go.mod, no purego build tag, and open issues #5 and #6 without a code change.

## How it is fast

On amd64, Bytes picks a hand-written Go assembly kernel at run time through golang.org/x/sys/cpu. The AVX2 kernel unrolls eight 32-byte VMOVDQU/VPXOR/VMOVDQU triples per 256-byte iteration and then steps down through 128-, 64- and 16-byte loops and a byte tail. The SSE2 kernel uses a 64-byte unrolled MOVOU/PXOR loop. The gain is plain SIMD width plus unrolling, because the gc compiler does not auto-vectorise. Block skips the assembly call, which Go can never inline: it casts the 16-byte slices to \*[2]uintptr so the compiler inlines it as two 64-bit xors. 386, ppc64, ppc64le and s390x get a word-wise Go loop built from unsafe slice-header casts. Every other architecture, arm64 included, gets a plain byte loop.

## Compared with alternatives

bwesterb/go-and also covers and, or, andn and popcount with AVX2 and arm64 NEON (README: Xor 82 GiB/s on an i9-13900, 58 GiB/s on an M2 Pro), so it is the better general choice. Pick fastxor only for amd64-only code that wants a tiny dependency with an inlinable 16-byte Block helper. Prefer the standard library's crypto/subtle.XORBytes over both unless a benchmark on your own hardware shows the AVX2 gain.

## Integration

| | |
|---|---|
| **Form** | module (single Go package without go.mod; also small enough to source-drop) |
| **Dependencies** | golang.org/x/sys/cpu (amd64 build only) |
| **Minimum toolchain** | Go 1.7+ with the gc compiler for the amd64 assembly path (build tag go1.7). Under gccgo or appengine on amd64, the build constraints exclude every implementation file, so the package does not build. |
| **Platforms** | amd64 (AVX2 or SSE2 assembly chosen at run time; word-wise Go fallback without SSE2); 386, ppc64, ppc64le and s390x (word-wise Go); everything else, including arm64 (byte-wise Go) |
| **Thread safety** | Not documented. The functions keep no state, so concurrent calls on distinct dst buffers are safe (inferred from the source). |
| **Drop-in for the baseline** | partial: Bytes(dst, a, b) int has the same signature as crypto/subtle.XORBytes and replaces a hand-written loop, but it truncates to len(dst) where the stdlib panics and it does not check overlap. Byte and Block have no stdlib equivalent. |

## Gotchas

- Block is memory-unsafe or wrong off the happy path. On amd64 it casts &dst[0], &a[0] and &b[0] to \*[2]uintptr without checking for 16 bytes, so shorter slices are read and written out of bounds silently (the generic xor.go version asserts dst[15]). On 386, the xor_unaligned.go Block xors two 4-byte uintptr words, so it processes only the first 8 of the 16 bytes. That is a correctness bug on GOARCH=386 that TestBlock would catch if it were ever run there.
- Byte on amd64 evaluates dst[n-1] without an n == 0 guard, so an empty input panics with index out of range [-1]. Commit 07dbf56 added that guard to xor.go but not to xor_amd64.go, and the tests skip inputs shorter than 8 bytes.
- The AVX2 kernel never issues VZEROUPPER. Its 16-byte tail also uses legacy-SSE MOVOU after 256-bit operations. Lengths of at least 64 that are not a multiple of 64 therefore run SSE code with dirty upper YMM state, and the dirty state leaks into the caller. That is a known transition or false-dependency penalty on many Intel cores. The benchmark sizes (16, 1024 and 65536 bytes) never take this path (inference from the code, not measured).
- Harness flaws behind the README. BenchmarkBytes calls Bytes(buf, buf, buf) on one zeroed buffer of at most 64 KiB, so all three operands alias, the data stays in L1/L2, and MB/s counts one stream. The 'about 6 times faster' Block claim divides a Block run from 2018-10-11 (1.18 ns, commit ab5bbce) by a Bytes/16 run from 2018-07-06 (6.20 ns). In the same 2018-07-06 run, Block took 2.72 ns, a 2.3x gain (derived from page data). The unchanged byte-wise and word-wise rows also shifted about 39% between the 2018-07-05 and 2018-07-06 README tables, so ratios across runs are unreliable.

## Known shortcomings

- No CPU or Go version; the 40x is against a bounds-checked byte loop and only 1.2-5.8x against a word-wise loop; the SSE row was measured before the segfault fix 62a404d; the AVX path was gated on HasAVX until 2021 (issue #2); crypto/subtle.XORBytes (SSE2 assembly) was never compared.
- Code bugs off the measured path: amd64 Block has no length check (out-of-bounds read and write on slices shorter than 16 bytes); 386 Block xors only 8 of 16 bytes; amd64 Byte panics on empty input; no VZEROUPPER, with a legacy-SSE tail after 256-bit ops. Harness flaws: BenchmarkBytes calls Bytes(buf, buf, buf) on one zeroed cache-resident buffer, so all operands alias; the 'about 6x' Block claim is cross-run (Block 1.18 ns from 2018-10-11, ab5bbce, vs Bytes/16 6.20 ns from 2018-07-06; the same-run ratio is 2.3x), and the unchanged byte-wise and word-wise rows shifted about 39% between the 2018-07-05 and 2018-07-06 tables. Issue #4 reports no gain at 64 B on a Core i5 with Go 1.16.

## Caveats and trade-offs

No CPU model, Go version or flags; GOMAXPROCS 4 is the only setup detail. The README's AVX/SSE/word-wise/byte-wise numbers were committed on 2018-07-06 (000cb37). The SSE row predates commit 62a404d ('fix SSE segfault', same day), which rewrote the SSE loops: the measured code XORed from memory operands that fault on unaligned input (the benchmark's buffers happened to be aligned). The AVX path was dispatched on cpu.X86.HasAVX while using 256-bit integer VPXOR, which needs AVX2. It crashed with an illegal instruction on AVX-only CPUs such as the i7-3770 (issue #2) until PR #3 on 2021-03-22. That bug did not affect the measured path. The 40x headline is against a byte-wise loop that, in 2018, still had per-iteration bounds checks (BCE hints were added in 43ff724, 2020). Against the word-wise loop the gain is 1.2-5.8x. The benchmark aliases dst, a and b to one zeroed buffer, so the working set is a third of a real three-buffer xor. The modern Go incumbent, crypto/subtle.XORBytes (exported in Go 1.20; its amd64 assembly is a 16-byte SSE2 loop), was not benchmarked. fastxor's own SSE row is the closer analogue, so the AVX2 gain over today's stdlib is plausibly about 2x, not 5-40x (inference, not measured). There is no VZEROUPPER after the AVX2 loop. The author calls it a first try at Go assembly. amd64 only; other architectures use plain Go loops. 12 commits, last change 2021-03-22. [retier] No CPU model, Go version or flags; GOMAXPROCS 4 is the only setup detail. Harness flaws: BenchmarkBytes calls Bytes(buf, buf, buf) on one zeroed buffer of at most 64 KiB, so all three operands alias, the data stays in L1/L2 and MB/s counts one stream; the unchanged byte-wise and word-wise rows shifted about 39% between the 2018-07-05 and 2018-07-06 tables; the Block claim is cross-run (struck). The SSE row predates commit 62a404d ('fix SSE segfault', same day), which rewrote the SSE loops; the AVX path was dispatched on cpu.X86.HasAVX while using AVX2 VPXOR and crashed on AVX-only CPUs (issue #2) until PR #3 (2021-03-22). Issue #4 reports no gain at 64 B on a Core i5 with Go 1.16. Code bugs off the measured path: amd64 Block casts to \*[2]uintptr without a 16-byte length check (silent out-of-bounds read and write on shorter slices); the 386 Block xors only 8 of 16 bytes; amd64 Byte panics on empty input (index -1); the AVX2 kernel never issues VZEROUPPER and runs a legacy-SSE tail after 256-bit ops, leaking dirty upper state into the caller for lengths of at least 64 that are not a multiple of 64 (not hit by the benchmark sizes). The 40x headline is against a byte-wise loop.

x86-64 AVX/SSE assembly with generic Go fallback (xor_unaligned.go); Go never inlines assembly, so tiny slices lose most of the gain.

## Maintenance

Abandoned (12 commits, last 2021-03-22, no go.mod) but MIT-licensed and small enough to vendor. Before relying on it, fix the 386 Block bug, the empty-slice Byte panic and the missing VZEROUPPER, and benchmark crypto/subtle.XORBytes first.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README benchmark blocks (AVX, SSE, word-wise and byte-wise runs of BenchmarkBytes; benchmark code is public in xor_test.go) with no CPU model, Go version or flags, so tier C. The SSE row was measured on assembly that was rewritten later the same day to fix a segfault, which also caps it at C.
- **Verifier notes:** README numbers match the record; the ratios are derived from page data. Main shortcomings: no hardware or Go version; the 40x figure is against a bounds-checked byte loop (5x against word-wise); the SSE row was measured on code later fixed for a segfault; and Go's crypto/subtle.XORBytes (SSE2 asm) was never compared. Not a duplicate of any catalog entry.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `hardware`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-70 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/lukechampine/fastxor>
  - <https://github.com/lukechampine/fastxor/commits>
  - <https://github.com/lukechampine/fastxor/commits/master/README.md>
  - <https://github.com/lukechampine/fastxor/commit/000cb37>
  - <https://github.com/lukechampine/fastxor/commit/62a404d>
  - <https://github.com/lukechampine/fastxor/commit/43ff724>
  - <https://github.com/lukechampine/fastxor/commit/041c0ef>
  - <https://github.com/lukechampine/fastxor/issues/2>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/README.md>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/xor.go>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/xor_amd64.go>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/xor_amd64.s>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/xor_test.go>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/xor_unaligned.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/crypto/internal/fips140/subtle/xor_amd64.s>
- **Sources the enricher read:**
  - <https://github.com/lukechampine/fastxor>
  - <https://github.com/lukechampine/fastxor/commits/master>
  - <https://github.com/lukechampine/fastxor/issues?q=is%3Aissue>
  - <https://github.com/lukechampine/fastxor/issues/4>
  - <https://github.com/lukechampine/fastxor/issues/5>
  - <https://github.com/lukechampine/fastxor/issues/6>
  - <https://github.com/lukechampine/fastxor/commit/000cb37>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/README.md>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/xor.go>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/xor_amd64.go>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/xor_amd64.s>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/xor_test.go>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/HEAD/xor_unaligned.go>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/a04e125/README.md>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/a04e125/xor_amd64.go>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/a04e125/xor_test.go>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/a04e125/xor_amd64.s>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/000cb37/README.md>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/000cb37/xor_amd64.go>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/000cb37/xor_test.go>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/000cb37/xor_amd64.s>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/62a404d/README.md>
  - <https://raw.githubusercontent.com/lukechampine/fastxor/ab5bbce/README.md>
  - <https://raw.githubusercontent.com/golang/go/master/src/crypto/internal/fips140/subtle/xor.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/crypto/internal/fips140/subtle/xor_amd64.s>
  - <https://raw.githubusercontent.com/golang/go/master/src/crypto/internal/fips140/subtle/xor_arm64.s>
  - <https://raw.githubusercontent.com/golang/go/master/src/crypto/internal/fips140/subtle/xor_asm.go>
  - <https://raw.githubusercontent.com/golang/go/master/src/crypto/internal/fips140/subtle/xor_generic.go>
  - <https://github.com/bwesterb/go-and>
  - <https://github.com/templexxx/xorsimd>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/lukechampine/fastxor`) · [data/wave13/enrich/raw/github_com_lukechampine_fastxor.json](../../../data/wave13/enrich/raw/github_com_lukechampine_fastxor.json) (enrichment confidence 0.8)

</details>
