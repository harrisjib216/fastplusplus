# gofiber/utils v2 simd package (AVX2 Memchr2, Memchr3, Memmem, IsASCII for Go)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Assembly-level string and memory routines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go (with Go assembly)` · `MIT` · 🟢 active

> Go package with AVX2 assembly multi-byte, class, ASCII and substring scans on []byte; beats bytes.ContainsAny, bytes.Index and its own SWAR loops above 64 bytes.

| | |
|---|---|
| **Beats** | Go standard library, per simd/bench_test.go: bytes.Contains (bytes.Index) for Memmem; bytes.ContainsAny(data, "zy") and bytes.ContainsAny(data, "zyx") for Memchr2 and Memchr3 (a per-byte ASCII-set loop, not a vectorised search); the package's own scalar loops (memchr2Generic, memchr3Generic) and SWAR fallbacks as second baselines. bytes.IndexByte is deliberately not wrapped because the Go runtime already vectorises it. |
| **Claimed result** | README amd64 table (go test ./simd/ -count=1): Memmem 4096 B 38.44 ns (simd) vs 921.5 ns (bytes.Contains), about 24x; 512 B 10.22 vs 119.8 ns, about 11.7x; 96 B 8.323 vs 20.11 ns, about 2.4x; slower up to 64 B (8 B 4.450 vs 3.551 ns). Memchr2 4096 B 26.22 ns vs 1572 ns for bytes.ContainsAny (about 60x) but vs 422.0 ns for the package's own scalar loop (about 16x); Memchr3 4096 B 35.38 vs 1620 ns ContainsAny (about 46x), vs 506.4 ns scalar (about 14x); IsASCII 4096 B 14.17 vs 46.72 ns SWAR (about 3.3x). All ratios derived from page data. README text also quotes benchstat -count=10 gains of -35% to -88% ns/op against the SWAR paths at 32-512 B. |
| **Workload** | simd/bench_test.go: synthetic haystacks of 8-4096 B filled with the repeating bytes 'a'..'w', worst-case misses so every variant scans the whole input; Memchr2/Memchr3 search for 'z','y'(,'x'); Memmem searches for the needle "q7z" (8-4096 B); IsASCII, FirstNonASCII, CountNonASCII, MemchrPair, MemchrDigit, MemchrWord scans; each reported as simd, scalar/swar and default (stdlib) rows in ns/op. |
| **Metric** | latency |
| **Hardware** | linux/amd64, cpu: AMD EPYC (exact model not stated), 4 threads (-4 suffix); arm64 catalog on Apple M2 Pro for the non-SIMD helpers. |
| **Compiler and flags** | Go toolchain version not stated (go.mod requires go 1.26.0, so 1.26 or later); go test ./simd/ -benchmem -run=^\$ -bench=Benchmark_ -count=1 |
| **Adoption** | 57 stars; used by the Fiber web framework |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/gofiber/utils) · [benchmark](https://raw.githubusercontent.com/gofiber/utils/HEAD/README.md) |

## Verdict

The README's single go test -count=1 run on linux/amd64 'AMD EPYC' (GOMAXPROCS 4, Go 1.26+, warm 8 B-4 KiB buffers, full-scan misses) shows the following. Memmem: 38.44 vs 921.5 ns for bytes.Contains at 4 KiB (24x) and 10.22 vs 119.8 ns at 512 B, but slower than bytes.Contains up to 64 B (8 B 4.45 vs 3.55 ns). Memchr2: 26.22 ns vs 422.0 ns for the SWAR loop (16x) and 1572 ns for bytes.ContainsAny (60x) at 4 KiB. ASCII scans at 4 KiB against the SWAR fallback: IsASCII 14.17 vs 46.72 ns (3.3x), FirstNonASCII 14.19 vs 108.7 ns (7.7x), CountNonASCII 17.36 vs 145.3 ns (8.4x). Ratios are derived from page data.

## Use it when

- Go services on amd64 with AVX2 that scan []byte payloads of hundreds of bytes to a few KiB for any of 2-3 delimiters, digits, \w or non-\w bytes, or non-ASCII bytes, for example HTTP header and query parsing in Fiber.
- Replacing bytes.ContainsAny or bytes.IndexAny with a 2-3 byte ASCII set on inputs of 64 bytes or more. At 512 B the README shows 4.2 ns vs 214 ns.
- Substring search with short needles (2-6 bytes, two distinct values) on 65+ byte haystacks where the needle's bytes are rare in the data: 96 B 8.3 vs 20.1 ns, 4 KiB 38 vs 922 ns against bytes.Contains.
- ASCII validation or counting non-ASCII bytes on inputs above 64 B: IsASCII 4 KiB 14.2 vs 46.7 ns, CountNonASCII 17.4 vs 145.3 ns against the SWAR fallback.

## Skip it when

- Inputs under about 64 bytes. Below 32 B the kernels never run, and the exported call is slower than the fallback it dispatches to (IsASCII 8 B 2.11 vs 0.95 ns, MemchrPair 8 B 5.21 vs 2.53 ns scalar). At 32-64 B, IsASCII, MemchrPair and Memmem are level or behind.
- Non-amd64 targets (arm64 and others) or CPUs without AVX2. Only SWAR fallbacks run there, with no NEON or SVE kernels.
- Memmem on data where the needle's 'rare' bytes are common, such as digits in numeric logs, high bytes in non-Latin UTF-8, or long needles anchored on frequent letters. The prefilter then exhausts its 16-miss budget and tracks bytes.Index: the README's single-rare-byte rows trail it (4 KiB 922.7 vs 863.5 ns), and the adversarial case is at parity (1.033 ms both).
- Single-byte search, or repeated searches for one needle. There is no Memchr (use bytes.IndexByte), and Memmem recomputes SelectRareBytes on every call; it has no prebuilt searcher.
- Projects on Go older than 1.26, since go.mod declares go 1.26.0.

## How it is fast

Each AVX2 kernel (Go assembly) handles four 32-byte vectors per iteration. It ORs the four compare masks so a 128-byte block costs one VPMOVMSKB and one branch, and finishes with an overlapping last vector instead of a scalar tail. The word-class test uses two VPSHUFB nibble-table lookups, and the digit test is one biased VPADDB plus one compare. CountNonASCII accumulates per-lane counts in byte lanes and flushes them through VPSADBW. Memmem is a rare-byte prefilter in the style of BurntSushi's memchr: SelectRareBytes ranks needle bytes with a fixed frequency table. Needles of 2-6 bytes are scanned with MemchrPair for their two rarest bytes at the exact distance, and longer needles with bytes.IndexByte for the rarest byte; the search falls back to bytes.Index after 16 failed verifications.

## Compared with alternatives

It is the only Go entry in this category for multi-byte memchr, class scans and memmem; sliceslice (Rust AVX2 substring search), memx-cdy (Rust memchr/memmem behind a C ABI) and WojciechMula's toys strstr (C++) serve other languages. Pick it in Go amd64 code that already depends on Fiber or wants vectorised IndexAny-style and ASCII scans without cgo; for single-byte search stay with bytes.IndexByte.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | golang.org/x/sys/cpu for AVX2/POPCNT detection, plus the module's own swar package; the utils/v2 module as a whole also requires fxamacker/cbor, google/uuid and shamaton/msgpack |
| **Minimum toolchain** | Go 1.26.0 (go.mod) |
| **Platforms** | amd64 with AVX2 for the kernels (CountNonASCII also needs POPCNT); portable SWAR fallback on every other GOARCH |
| **Thread safety** | Stateless functions on caller slices. The CPU flags are read once at package init, and the frequency table is unexported and read-only, so concurrent use is safe. |
| **Drop-in for the baseline** | partial — Memmem returns the same index as bytes.Index (fuzzed against it), so it can replace bytes.Index or bytes.Contains on []byte. Memchr2 and Memchr3 take byte arguments rather than bytes.IndexAny's UTF-8 chars string, so they match it only for ASCII sets. Package simd has no string variants; the top-level utils generics cover strings. |

## Gotchas

- The headline 60x (Memchr2) and 46x (Memchr3) are measured against bytes.ContainsAny, a per-byte set loop. The rows labelled 'scalar' are actually the package's own 8-byte SWAR word loops (memchr2Generic uses swar.ZeroLanes), not byte loops: 16x and 14x at 4 KiB. The fairer stdlib idiom, two vectorised bytes.IndexByte passes, is not benchmarked.
- Benchmark harness (simd/bench_test.go): results are checked, so calls are not optimised away. But every row reuses one warm buffer of at most 4 KiB, only full-scan misses are timed, and the table is one -count=1 run on an unnamed 'AMD EPYC' with GOMAXPROCS=4. The README says small rows drifted up to 17% between runs. The Memmem needle "q7z" has two bytes that never occur in the 'a'..'w' haystack, which is the best case for the paired prefilter. The 4 KiB IsASCII row (14.17 ns, about 289 bytes/ns) is L1 load bandwidth, not memory bandwidth.
- A latent out-of-bounds read existed in the AVX2 count kernel. Commit 21ac610 (2026-07-29) fixed countNonASCIIAVX2's loop test (base &lt; end instead of base &lt;= end-32), which could read up to 24 bytes past a 40-byte slice and SIGSEGV at a page end. The only caller masked the length, so the tests missed it. A Test_KernelsAreSelfBounding guard and POPCNT gating were added, and fuzz targets compare every exported function against references and bytes.Index.
- The README explains a 10% MemchrPair swing as Intel's Skylake JCC-erratum effect and pins block loops with a BLOCKALIGN macro, but the published runs are on an AMD EPYC. Code alignment still moves results, so treat small deltas between builds as noise.

## Known shortcomings

- The Memchr2/3 "default" row is bytes.ContainsAny (scalar), so the 60x headline drops to about 16x against the package's own scalar loop; the Memmem needle "q7z" favours the prefilter; single run on an unnamed EPYC with Go 1.26+. Go-only.
- Enricher: the 'scalar' bench rows are SWAR word loops and the 60x/46x are only against bytes.ContainsAny while the two-pass bytes.IndexByte alternative is never benchmarked; one warm buffer of at most 4 KiB, -count=1, best-case 'q7z' needle; an out-of-bounds read in countNonASCIIAVX2 (up to 24 B past the slice, possible SIGSEGV) was fixed in commit 21ac610; the simd package was added 2026-07-21 with all its commits by an AI-agent account; the JCC-erratum explanation cites Intel while the runs are on AMD EPYC. Lead: coregx/coregex (Go regex engine claiming 3-3000x vs regexp).

## Caveats and trade-offs

Baseline is the Go standard library, not glibc or musl. The 60x Memchr2 and 46x Memchr3 ratios are against bytes.ContainsAny, a per-byte ASCII-set loop with setup overhead (15.47 ns even at 8 B), not against a vectorised stdlib path; against the package's own scalar loop the gain is about 16x and 14x at 4096 B. The Memmem benchmark is favourable to the paired prefilter: two of the needle's three bytes ('7', 'z') never occur in the 'a'..'w' haystack, so the prefilter never produces a candidate while bytes.Index anchors on 'q' every 23 bytes; when the anchor byte is common the single-rare-byte path tracks or trails bytes.Index (Benchmark_Memmem_Prefilter 4096 B single 922.7 ns vs 863.5 ns stdlib), and the adversarial case is at parity. Numbers are one run (-count=1) on an unspecified EPYC model with an unstated Go 1.26+ toolchain and GOMAXPROCS=4; the README itself warns that small-input rows drifted up to 17% between runs. Per-commit benchmark charts live on gofiber.github.io (blocked here). The kernels are adapted from the coregx/coregex simd package (MIT, simd/LICENSE), so part of the design is upstream. Inputs under 32 bytes never reach the AVX2 kernels, and Memmem delegates to bytes.Index up to 64 bytes. AVX2 path is amd64-only.

AVX2 kernels engage only on amd64 for inputs of 32 bytes or more (simd.MinLen); portable SWAR fallbacks elsewhere; []byte only; no single-byte Memchr because bytes.IndexByte is already vectorised; Memmem delegates to bytes.Index up to 64 bytes and bails to it after a bounded number of failed candidates.

## Maintenance

Active and MIT-licensed (last commit 2026-10-11, tags up to v2.6.1 on 2026-09-24, 860 commits, coregex MIT notice in simd/LICENSE). The simd package is young: it was added 2026-07-21, adapted from coregx/coregex, and every commit in its history is authored by an AI coding-agent account ('claude'). Review it before relying on it outside Fiber.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party single-run go test numbers in the README from public benchmark code (simd/bench_test.go) on an unnamed 'AMD EPYC' with no exact Go toolchain version, so not A; no independent or peer-reviewed measurement, so C.
- **Verifier notes:** Numbers in the record match the README, but the Memchr2/Memchr3 'default' baseline is bytes.ContainsAny (scalar per-byte set lookup), which inflates the 60x figure; corrected baseline, claimed_speedup and caveats, and noted the favourable Memmem needle. MIT, 57 stars, last commit 2026-10-11, not archived. Shortcomings: weak ContainsAny baseline, synthetic best-case Memmem needle, single-run unnamed EPYC, slower below 32-64 B.
- **Fields the verifier corrected:** `baseline`, `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-63 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/gofiber/utils>
  - <https://github.com/gofiber/utils/commits>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/README.md>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/bench_test.go>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/simd_test.go>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/LICENSE>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/go.mod>
- **Sources the enricher read:**
  - <https://github.com/gofiber/utils>
  - <https://github.com/gofiber/utils/tags>
  - <https://github.com/gofiber/utils/tree/master/simd>
  - <https://github.com/gofiber/utils/commits/master/simd>
  - <https://github.com/gofiber/utils/commit/21ac610>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/README.md>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/go.mod>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/bench_test.go>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/simd_test.go>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/LICENSE>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/simd.go>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/cpu_amd64.go>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/cpu_other.go>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/memchr.go>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/memchr_amd64.go>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/memchr_amd64.s>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/memmem.go>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/ascii_amd64.go>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/ascii_amd64.s>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/byte_frequencies.go>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/fuzz_test.go>
  - <https://raw.githubusercontent.com/gofiber/utils/HEAD/simd/guard_amd64_test.go>
  - <https://github.com/coregx/coregex>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/gofiber/utils`) · [data/wave13/enrich/raw/github_com_gofiber_utils.json](../../../data/wave13/enrich/raw/github_com_gofiber_utils.json) (enrichment confidence 0.65)

</details>
