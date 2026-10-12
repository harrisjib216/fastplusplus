# vectorcmp (hexon)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go (AVX2 assembly, generated with avo)` · `BSD-2-Clause` · 🟡 stale

> Go AVX2 assembly comparing one value against a column into a bitmask; 5-232x faster than its scalar Go loop.

| | |
|---|---|
| **Beats** | pure-Go scalar loop that sets one bit per matching element (build tag purego), compiled by the Go gc compiler |
| **Claimed result** | README benchstat table (i9-14900, n=10, re-measured in the 2025-10-03 bugfix commit cb1b7b5), purego vs avx2 sec/op: VectorEquals8 145594.5ns -&gt; 628.0ns (-99.57%, about 232x derived from page data); VectorEquals16 151.078us -&gt; 1.325us (-99.12%); VectorEquals32 146.441us -&gt; 2.626us (-98.21%); VectorEquals64 146.577us -&gt; 4.468us (-96.95%); VectorGreaterThan8 146456.5ns -&gt; 856.9ns (-99.41%); geomean over all 38 rows 133.0us -&gt; 2.492us (-98.13%, about 53x derived from page data). The IsNaN rows, where the scalar branch is predictable, show only 23.555us -&gt; 2.228us (float32, about 10.6x derived from page data) and 23.687us -&gt; 4.410us (float64, about 5.4x derived from page data). |
| **Workload** | comparison of one search value against 65,536 + rand(0..2047) elements of uint8/16/32/64 or float32/64 (Equals, NotEquals, GreaterThan, LessThan, GreaterEquals, LesserEquals, IsNaN) producing a bit-packed result mask with AVX2 VPCMP (AVX1 fallback); test data is drawn from three values ('a', 'b', 'c'; search 'b') plus 20 max-value or NaN entries |
| **Metric** | latency |
| **Hardware** | 14th Gen Intel Core i9-14900 |
| **Compiler and flags** | go test -bench compared with benchstat (n=10, p=0.000); purego column is the scalar Go fallback (purego build tag), avx2 column the default amd64 build with runtime AVX2+BMI2 dispatch; GOMAXPROCS 32 (-32 suffix); Go toolchain version not stated (go.mod says go 1.18) |
| **Adoption** | 4 stars |
| **Last commit** | 2025-10-05 |
| **Links** | [repository](https://github.com/hexon/vectorcmp) · [benchmark](https://github.com/hexon/vectorcmp) |

## Verdict

The README's benchstat table (n=10, i9-14900, GOMAXPROCS 32, Go version not stated) runs the same benchmarks built with the purego tag (scalar Go loop, gc compiler) and with the default AVX2 dispatch. Each run uses 65,536-67,583 random elements drawn from 'a'/'b'/'c' with search 'b'. 8-bit Equals drops from 145.6 us to 0.628 us (about 232x), 64-bit Equals from 146.6 us to 4.47 us (about 33x), and the geomean is 133.0 us to 2.49 us (about 53x). The IsNaN rows, where the scalar branch is predictable, give 10.6x (float32) and 5.4x (float64) (derived from page data).

## Use it when

- In-memory columnar filtering in Go: evaluating `column <op> constant` over unsigned or float slices of thousands of rows or more to build a selection bitmap.
- amd64 hosts with AVX2 and BMI2 (Haswell and Zen or newer); build with GOAMD64=v3 to drop the run-time feature check.
- Predicates whose match pattern defeats branch prediction. With about one third random matches the README shows 53x geomean and 232x for 8-bit Equals over the scalar loop on an i9-14900.
- Scanning float columns for NaNs: VectorIsNaNFloat32 and VectorIsNaNFloat64 are 10.6x and 5.4x even against a well-predicted scalar loop (derived from page data).
- When you want a tiny, vendorable dependency: BSD-2-Clause, the only run-time dependency is golang.org/x/sys, and the assembly is generated and checked in.

## Skip it when

- arm64 and other non-amd64 targets: they get only the scalar loop (CI just checks that arm64 builds), and there is no NEON or AVX-512 path.
- Signed integer columns with ordered comparisons. Only unsigned and float element types exist, and reinterpreting int32 as uint32 makes negative values compare as large. Equals and NotEquals still work after a reinterpret cast.
- Short slices. Below 64 (8-bit), 32 (16-bit) or 16 (32/64-bit) rows the AVX2 path is skipped, and any remainder runs through the scalar loop.
- Range predicates, multi-column filters, or accumulating into an existing bitmap. Each call rewrites dst from bit 0 and zeroes its unused tail, so you have to AND or OR the separate bitmaps yourself.
- Columns much larger than cache. The benchmark's 66-533 KB inputs are cache-resident, so gains on DRAM-resident data will be capped by memory bandwidth; this was not measured. Also avoid versions before cb1b7b5 (2025-10-03), whose ordered unsigned comparisons were wrong for values with the top bit set.

## How it is fast

Each kernel loads 2 or 4 YMM registers per iteration (64 bytes for 8-bit and 16/32-bit lanes, 128 bytes for 64-bit lanes) and compares them against a broadcast of the search value. Integers use VPCMPEQ/VPCMPGT; unsigned ordering is done by XOR-flipping the sign bit of both sides. Floats use VCMPPS/VCMPPD with ordered or unordered quiet predicates that match Go's NaN semantics. VPMOVMSKB packs the compare results into a general register, BMI2 PEXT drops the duplicate bits for 16/32/64-bit lanes, and whole bytes are stored to dst. Missing predicates come from swapping operands and NOT-ing the mask. The assembly is produced by an avo generator (internal/avo/avo.go). An AVX1 128-bit variant uses VPSHUFB instead of PEXT, and the dispatcher picks a path at run time through golang.org/x/sys/cpu, or at compile time with GOAMD64=v3, then sends the tail to the scalar loop.

## Compared with alternatives

Pick it when you need a per-row predicate bitmap from a numeric column. go-byte-test only answers whether all bytes equal one value, so it is not a substitute. go-and (bitmap AND/OR/XOR) and go-popcount or pospop (counting set bits) are the natural next steps in the same filter pipeline, not alternatives.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/sys (CPU feature detection); github.com/mmcloughlin/avo v0.6.0 only to regenerate the assembly |
| **Minimum toolchain** | Go 1.18 per go.mod (generics); CI builds and tests with Go 1.20; regenerating the assembly needs Go 1.22.5 per internal/avo/go.mod |
| **Platforms** | amd64 with AVX2+BMI2 (256-bit path) or AVX only (128-bit path); every other GOARCH and the purego build tag use the scalar loop |
| **Thread safety** | Not documented. The functions keep no state (CPU flags are read once at package init) and write only to the caller's dst slice, so concurrent calls with separate dst buffers are safe by construction. |
| **Drop-in for the baseline** | yes |

## Gotchas

- Operand order reads backwards from SQL: VectorGreaterThan sets bit i when search &gt; rows[i], so it selects rows less than search, and VectorLessThan selects rows greater than search. The godoc says this, but the names invite the opposite reading.
- dst must hold at least len(rows) bits, or the call panics with 'vectorcmp: given bitmap is not large enough to hold bits for all rows'. The bounds check was only added before the assembly call in 2ef0089 (2025-03-04); older versions could write past a short dst. NaN handling was fixed in 86570d6 (2024-10-30) and unsigned ordering in cb1b7b5 (2025-10-03), so pin a recent commit.
- Tests compare the assembly against the scalar loop 500 times in each of four CI configurations (default, GOAMD64=v3, AVX1 tag, purego). Every input uses only the values 'a'/'b'/'c', the type maximum and NaN, with search always 'b' and lengths of 65,536-67,583, so short slices and other search values (0, max, NaN as the search) are never exercised. Reading the generated kernels found the predicate codes, operand order and bit packing consistent with the scalar loop; no bug was found.
- Harness flaw: the baseline is the library's own branchy scalar Go loop, run on data with about one-third random matches, so it costs about 2.2 ns per element, against about 0.35 ns per element in the well-predicted IsNaN rows. Using the IsNaN scalar time (about 23.6 us) as a proxy for a predictable-branch loop, the SIMD gain is roughly 25-38x for 8-bit, 13-18x for 16-bit, 7-11x for 32-bit and 3.5-5.4x for 64-bit lanes (derived from page data, cross-row estimate), not 53-232x. The table also predates the 2025-10-04/05 optimisation commits f74d5a7 and 3ff822d.

## Known shortcomings

- Baseline is a branchy scalar Go loop on random 1-in-3 matches, so branch mispredictions dominate; the predictable-branch IsNaN rows give only 10.6x/5.4x against the 232x headline; Go version unstated; assembly generated by avo; the table was re-measured in bugfix commit cb1b7b5.
- Harness flaw: the baseline is the library's own branchy scalar Go loop on data with about one-third random matches (about 2.2 ns per element versus 0.35 ns in the predictable IsNaN rows); using the IsNaN scalar time as a predictable-branch proxy gives roughly 25-38x for 8-bit, 13-18x for 16-bit, 7-11x for 32-bit and 3.5-5.4x for 64-bit lanes (derived from page data), not 53-232x. Kernels read: predicate codes, operand order, unsigned XOR trick and PEXT packing match the scalar loop. VectorGreaterThan means search &gt; rows[i]; NaN (86570d6), bounds check (2ef0089) and unsigned (cb1b7b5) fixes landed late; tests use only a/b/c, max and NaN data with search always 'b' at lengths 65,536-67,583; the README table predates f74d5a7 and 3ff822d.

## Caveats and trade-offs

The baseline is the library's own naive scalar Go loop (gc compiler, no auto-vectorisation) with a data-dependent branch and a read-modify-write of the output byte per element. The test data matches the search value about one time in three at random, so that branch mispredicts heavily: the scalar Equals8 row costs about 2.2 ns per element, while the IsNaN rows (20 NaNs, predictable branch) cost about 0.35 ns per element and give only 10.6x (float32) and 5.4x (float64) (derived from page data). The 97-99.6% reductions therefore mostly measure branch mispredictions, not SIMD versus good (branchless or SWAR) scalar code, and there is no C/C++ -O3 baseline. The assembly is generated by internal/avo (asm_amd64.s and dispatch_amd64.go say 'Code generated by avo.go. DO NOT EDIT.'), with instructions chosen by hand in the avo DSL. The README table was re-measured in commit cb1b7b5 (2025-10-03, 'Bugfix: we accidentally did signed comparisons instead of unsigned'), so it postdates that correctness fix; two later optimisation commits (2025-10-04/05) are not reflected. README row names (VectorEquals8-32) do not match the current benchmark functions (BenchmarkAsmVectorEquals8 and BenchmarkGoVectorEquals8), so the table came from renamed or restructured runs. Buffer length is random per run (up to 3% different between columns). The Go Reference badge points at github.com/Jille/vectorcmp, a 0-star fork of this repo; the module path in go.mod is github.com/hexon/vectorcmp. amd64 only; other architectures use the scalar loop.

amd64 AVX2 only, with runtime detection and a pure-Go fallback; result is a packed bitmask, so callers must consume bitmaps; array sizes fixed by the benchmark.

## Maintenance

Stale (last commit 2025-10-05, 29 commits, 4 stars), but small, BSD-2-Clause, dependent only on x/sys and CI-tested in four build configurations, so it is easy to vendor. The headline numbers are inflated by a branch-mispredicting scalar baseline, which is the main harness flaw, and the README's Go Reference badge points at the Jille/vectorcmp fork rather than the github.com/hexon/vectorcmp module path.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README benchstat table (purego vs avx2, n=10, 14th Gen Intel Core i9-14900) from the repo's own benchmarks in generated_test.go (BenchmarkAsm\*/BenchmarkGo\*, inputs from helpers_test.go randomBuffer); CPU is stated but the Go toolchain version is not, so it falls short of A and stays first-party C.
- **Verifier notes:** Numbers match the README exactly; tier C stands. Main shortcoming for the orchestrator: the baseline is a branchy scalar Go loop on data that defeats branch prediction, so the 232x headline overstates the SIMD gain (predictable-branch IsNaN rows give 5.4-10.6x); Go version unstated; asm is avo-generated; last commit 2025-10-05 is just over 12 months old, so 'stale' is right.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-73 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/hexon/vectorcmp>
  - <https://github.com/hexon/vectorcmp/commits>
  - <https://github.com/hexon/vectorcmp/commits/master/README.md>
  - <https://github.com/hexon/vectorcmp/commit/cb1b7b5>
  - <https://github.com/Jille/vectorcmp>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/README.md>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/purego.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/helpers_test.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/generated_test.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/dispatch_amd64.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/detect_avx2_runtime.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/go.mod>
- **Sources the enricher read:**
  - <https://github.com/hexon/vectorcmp>
  - <https://github.com/hexon/vectorcmp/commits/master>
  - <https://github.com/hexon/vectorcmp/blob/master/helper.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/README.md>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/go.mod>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/go.sum>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/purego.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/helper.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/helpers_test.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/generated_test.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/dispatch_amd64.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/dispatch_other.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/stubs_amd64.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/typeswitch.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/asm_amd64.s>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/detect_avx2_runtime.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/detect_avx2_always.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/detect_avx2_never.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/detect_avx2_testing.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/internal/avo/avo.go>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/internal/avo/go.mod>
  - <https://raw.githubusercontent.com/hexon/vectorcmp/HEAD/.github/workflows/go.yml>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/hexon/vectorcmp`) · [data/wave13/enrich/raw/github_com_hexon_vectorcmp.json](../../../data/wave13/enrich/raw/github_com_hexon_vectorcmp.json) (enrichment confidence 0.7)

</details>
