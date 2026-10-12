# klauspost/compress fse and huff0 packages (Go tANS and Huffman)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [Entropy coders](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `BSD-3-Clause` · 🟢 active

> Pure-Go deflate/gzip/zlib/zip, zstd and S2 packages; deflate about 2x Go stdlib, S2 beats Go Snappy.

| | |
|---|---|
| **Beats** | Huffman (Go deflate Huffman coding stage) |
| **Claimed result** | README: deflate packages 'Typical speed is about 2x of the standard library packages' (no table; 'only minor speedup on decompression'); lzw '1.4-4x faster decompression and 1.1-2.7x faster compression' than compress/lzw. s2/README.md mixed web corpus (4,014,735,833 bytes, single goroutine): S2 936.73 MB/s at 73.60% reduction vs Snappy 790.15 MB/s at 71.89% and LZ4 452.02 MB/s at 73.50%; S2 Better 451.10 MB/s at 76.05%. Stream compression vs Snappy on a 16 core (32 thread) machine: 8.55x-22.00x using all threads (e.g. github-june-2days-2019.json 16.51x at 15224 MB/s, sofia csv 22.00x) because S2 streams compress concurrently and Snappy does not; on 1 CPU 0.88x-1.91x (slower than Snappy on 10gb.tar 0.97x and sharnd.out.2gb 0.88x; 'better' mode 0.27x-0.77x on 1 CPU). |
| **Workload** | FSE (tANS) encoding and decoding of byte blocks of about 64 KB, per core, compared with deflate Huffman encoding and decoding on the same hardware. |
| **Metric** | throughput |
| **Hardware** | unstated ("the same hardware") |
| **Adoption** | 5.7k stars (whole repository) |
| **Last commit** | 2026-10-02 |
| **Links** | [repository](https://github.com/klauspost/compress) · [benchmark](https://github.com/klauspost/compress/blob/master/fse/README.md) |

## Verdict

First-party README numbers, Go toolchain and flags unstated: S2 compresses a 4 GB web-page corpus at 936.73 MB/s single-goroutine vs Go Snappy at 790.15 MB/s with a 73.60% vs 71.89% size reduction; on a 16-core (32-thread) machine S2 streams are 8.55x-22x faster than single-threaded Go Snappy because they compress concurrently, while on 1 CPU the range is 0.88x-1.91x. The deflate packages claim 'about 2x' Go stdlib with no table in the README (a linked spreadsheet), and the Snappy baseline is the Go implementation, not Google's C++ library.

## Use it when

- Go services that call compress/gzip or compress/flate on a hot path (HTTP responses, log shipping) and want roughly 2x compression speed by changing an import.
- Replacing github.com/golang/snappy: S2 decodes existing Snappy data and, with Snappy-compatible output, writes data Snappy readers accept, faster and smaller (936.6 vs 790.15 MB/s on the 4 GB web corpus).
- Large streams on many-core amd64/arm64 hosts where concurrent S2 or zstd stream compression can use all cores (S2 streams 6.5-16.7 GB/s on a 16-core machine).
- Pure-Go zstd without cgo, for example in static or cross-compiled binaries.

## Skip it when

- C or C++ projects: there is no C API, and the C/C++ siblings (zlib-ng, libdeflate, zstd, LZ4) are the right choice there.
- Deflate decompression speed: the README says the gain on decompression is minor (mostly CRC32).
- Single-core S2 'better' mode when speed matters: it runs at 0.27x-0.77x of Snappy on one CPU, and default S2 is slower than Go Snappy on 10gb.tar (0.97x) and random data (0.88x).
- New S2 designs: the S2 README says the author considers MinLZ the better basis and expects only bug fixes for S2.
- Pinning old releases: correctness fixes land often (see gotchas) and security fixes go only to the latest release.

## How it is fast

Deflate levels 1-6 are replaced by specialised single-pass hash-table matchers (only levels 7-9 keep zlib-style lazy hash chains) with rebalanced levels, and decompression gains come mostly from a faster CRC32. S2 prefers matches of 6 bytes or longer, uses amd64 and arm64 assembly encoders/decoders, and splits streams into blocks compressed concurrently on all cores. zstd and huff0 use avo-generated amd64/arm64 assembly for sequence and literal decoding, and stream encode/decode is pipelined across goroutines.

## Compared with alternatives

Pick it when the codebase is Go and the baseline is Go's compress/\* or golang/snappy; for C/C++ use zlib-ng or libdeflate for deflate, facebook/zstd for zstd, and google/snappy or LZ4 for fast LZ. For new fast-LZ work in Go, the same author's MinLZ (sibling) supersedes S2.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (go.mod has no require block; helpers such as internal/le and xxhash are bundled) |
| **Minimum toolchain** | go.mod declares go 1.25; README: supports the current Go version and 2 versions back |
| **Platforms** | any Go target; assembly fast paths on amd64 and arm64 (disable with -tags=noasm; -tags=nounsafe removes unsafe); S2 README: not optimized for 32-bit systems |
| **Thread safety** | Writers/Readers are single-stream objects; zstd Encoder.EncodeAll and Decoder.DecodeAll may be called concurrently on one instance; SECURITY.md warns that not all functionality is re-entrant and safe to use concurrently. |
| **Drop-in for the baseline** | partial — flate/gzip/zlib/zip/lzw are import-path drop-ins for the Go stdlib with the same API and format; S2 output is not readable by Snappy unless Snappy-compatible mode is used; none of it replaces C zlib. |

## Gotchas

- Correctness history: zstd 'rare CORRUPTION output in best mode' fixed in v1.17.2 (PR 876); flate BestCompression produced undecodable output in v1.18.1 (issue 1114, 'flate: corrupt input before offset 10' on about 1 MiB of input), so v1.18.1 is retracted in go.mod together with v1.14.1-v1.14.3; earlier rare zstd corruption fixes in v1.9.0 and v1.9.6.
- Memory safety in the assembly paths has needed several fixes: s2 'occasional out-of-bounds write on amd64', s2 final-emit OOB read (PR 601), s2 amd64 stack frame corruption (PR 1145, v1.18.6), s2 NewDict out-of-bounds read (v1.18.7 security release), zstd decoder crash on amd64 without BMI on invalid input (PR 645). Build with -tags=noasm if you distrust the assembly.
- Concurrent stream modes spawn goroutines: call Close on zstd Readers to stop them, and set WithEncoderConcurrency(1) or WithDecoderConcurrency(1) for synchronous behaviour.
- Rebalanced deflate levels mean level N does not give the same speed/ratio as stdlib or zlib level N; stateless mode (level -3) gives ratios worse than level 1.

## Known shortcomings

- Go, not C++. The S2 claim is overstated: 16-core S2 vs Snappy runs 8.55x-22.00x, while single-core runs are 0.88x-1.91x and slower than Snappy on 10gb.tar and sharnd. Deflate 'about 2x' vs the Go stdlib has no table. LICENSE also carries Apache-2.0 and MIT sections.
- Go only, so C++ needs a cgo shim. The S2 baseline is Go Snappy (golang/snappy), not Google's C++ Snappy. Corruption history: zstd best-mode corruption fixed in v1.17.2; flate BestCompression produced undecodable output in v1.18.1 (issue 1114, release retracted in go.mod). Assembly memory-safety fixes: s2 out-of-bounds write on amd64, s2 stack frame corruption (PR 1145), s2 NewDict out-of-bounds read (v1.18.7), zstd no-BMI crash (PR 645). S2 is now maintenance-only; MinLZ supersedes it.

## Caveats and trade-offs

The baseline is Go's standard library, not C zlib; the \~2x deflate claim has no table and decompression gains are 'minor'. The 16-core S2 vs Snappy multiples mostly measure S2's concurrent stream compression against single-threaded Snappy; single-core S2 ranges 0.88x-1.91x and is slower than Snappy on two of ten files. No Go version or flags; CPU model not named for the compression table (Ryzen 3950X named only for decompression scaling); the LZ4 row in the corpus table does not name its implementation. LICENSE bundles BSD-3-Clause (main), Apache-2.0 and MIT sections for some subpackages/files (e.g. s2/cmd/internal/filepathx MIT), all OSI-approved.

Go only, not callable from C++ without cgo. Block-level API with no integrity checks. Speed depends on block size and on the highest byte value in the input. The huff0 package (README at huff0/README.md) is a port of the Huff0 codec from FiniteStateEntropy; it carries no speed numbers of its own.

## Maintenance

Very active (releases 1.20.0 and 1.20.1 in September 2026, last commit 2026-10-02), BSD-3-Clause with some Apache-2.0/MIT files, widely used in Go; the S2 package is in maintenance mode in favour of MinLZ.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): downgrade; tier before verification C, tier now C.
- **Tier reason:** First-party README tables (s2/README.md) compare S2 with Snappy and LZ4 on named corpora; the deflate-vs-Go-stdlib claim is a one-line 'about 2x' with no table. No Go version, flags or CPU model for the compression table, so C.
- **Verifier notes:** Numbers verified in s2/README.md; the record overstated the 16-core range ('up to 16.5x', table goes to 22.00x) and the single-core range ('1.05x-1.91x', table goes down to 0.88x), corrected. Metadata: 5.7k stars, not archived, last commit Oct 2, 2026.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `caveats`
- **Shortcomings recorded by:** first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/klauspost/compress>
  - <https://github.com/klauspost/compress/commits>
  - <https://raw.githubusercontent.com/klauspost/compress/HEAD/README.md>
  - <https://raw.githubusercontent.com/klauspost/compress/HEAD/s2/README.md>
  - <https://raw.githubusercontent.com/klauspost/compress/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/klauspost/compress/HEAD/README.md>
  - <https://raw.githubusercontent.com/klauspost/compress/HEAD/s2/README.md>
  - <https://raw.githubusercontent.com/klauspost/compress/HEAD/zstd/README.md>
  - <https://raw.githubusercontent.com/klauspost/compress/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/klauspost/compress/HEAD/go.mod>
  - <https://raw.githubusercontent.com/klauspost/compress/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/klauspost/compress/HEAD/flate/deflate.go>
  - <https://raw.githubusercontent.com/klauspost/compress/HEAD/s2/encode.go>
  - <https://raw.githubusercontent.com/klauspost/compress/HEAD/zstd/encoder.go>
  - <https://github.com/klauspost/compress/issues/1114>
  - <https://github.com/klauspost/compress/issues?q=is%3Aissue+is%3Aopen+label%3Abug>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/klauspost/compress`) · [data/wave9/enrich/raw/github_com_klauspost_compress.json](../../../data/wave9/enrich/raw/github_com_klauspost_compress.json) (enrichment confidence 0.8)

</details>
