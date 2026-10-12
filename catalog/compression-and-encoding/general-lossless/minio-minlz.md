# MinLZ

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Go` · `Apache-2.0` · 🟢 active

> Go LZ77 compressor (new byte-aligned format, Snappy/S2 successor) that compresses faster and smaller than LZ4's fastest mode.

| | |
|---|---|
| **Beats** | LZ4 (also compared with Snappy, S2 and gzip) |
| **Claimed result** | README: 'fastest mode typically beats LZ4 both in speed and output size'; protobuf block: MinLZ 1 27,837 MB/s compress and 17,613 bytes vs LZ4 0 12,649 MB/s and 18,766 bytes (but decompression 116,762 vs LZ4 137,553 MB/s, 'LZ4 is decompression speed king'); JSON stream of 6,273,951,764 bytes: MinLZ 1 14,921 MiB/s compress, 84.47% reduction, 3,204 MiB/s decompress vs LZ4 Fastest 5,860 MiB/s, 79.69%, 2,680 MiB/s and LZ4 Best 1,772 MiB/s, 82.60%, 2,694 MiB/s |
| **Workload** | Block compression of Snappy testdata files (e.g. protobuf, 16 concurrent threads) and compression of multi-GB streams (6.27 GB JSON, 2.6 GB Apache log, others) with the package's own concurrency |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 3950X 16-Core Processor, 16 concurrent threads for blocks; stream tests use the packages' concurrency |
| **Compiler and flags** | Go with AMD64 and ARM64 assembly; Go version and flags not stated |
| **Adoption** | 155 stars |
| **Last commit** | 2026-10-03 |
| **Links** | [repository](https://github.com/minio/minlz) · [benchmark](https://github.com/minio/minlz#readme) |

## Verdict

First-party README tables on an AMD Ryzen 9 3950X: on the Snappy-testdata protobuf block with 16 concurrent threads, MinLZ 1 compresses at 27,837 MB/s to 17,613 bytes vs LZ4 level 0 at 12,649 MB/s and 18,766 bytes, while LZ4 decodes faster (137,553 vs 116,762 MB/s); on a 6.27 GB JSON stream using each package's own concurrency, MinLZ 1 compresses at 14,921 MiB/s and decodes at 3,204 MiB/s vs LZ4 Fastest at 5,860 and 2,680 MiB/s. Go version, build flags and the LZ4 implementation/binding are not stated, and the identical 12,649 MB/s for LZ4 0 and LZ4 9 looks like a table copy error.

## Use it when

- Go services that compress on the hot path (RPC payloads, caches, object storage, logs) where Snappy or S2 is in use and you can change the wire format: same API shape, smaller output, and old Snappy/S2 data still decodes.
- Multi-GB streams on many-core machines where compression throughput matters more than ratio: the README's 6.27 GB JSON stream shows MinLZ 1 at 14,921 MiB/s and 84.47% reduction vs LZ4 Fastest at 5,860 MiB/s and 79.69% (16-core Ryzen 9 3950X, package concurrency).
- Seekable compressed streams: independent blocks plus an optional index allow random access and parallel decode without an external container.
- Mostly-text or structured data (JSON, CSV, logs, protobuf) where an 'always on' compressor should run near memory bandwidth; it detects already-compressed data quickly and stores it.

## Skip it when

- C++ projects: the maintained implementation is Go (plus Rust ports); the only C port is an experimental, machine-converted CC0 gist (block format only, 'not production level code').
- Decompression-bound workloads on small cached blocks: the README itself says 'LZ4 is decompression speed king' (protobuf block: LZ4 0 at 137,553 MB/s vs MinLZ 1 at 116,762 MB/s, 16 threads).
- Interchange with tools that expect LZ4, Snappy or gzip: MinLZ is a new format with no external decoders beyond its own ports.
- Archival or ratio-first storage: no entropy coding, so zstd gives smaller output; the spec itself points long-term storage to zstd. Level 3 also compresses slowly (210 MB/s on the protobuf block, 576 MiB/s on the JSON stream).
- Raw blocks without your own checksum: the block API does no integrity check; only the stream format carries checksums and EOF markers.

## How it is fast

The format has no entropy coding and no table-driven or context-dependent decoding: four tag types (literal/repeat, 10-bit, 16-bit and up-to-21-bit offset copies) with fused literal+copy forms, so a decoder is a branch-predictable byte loop. Copy2/Copy3 forbid offsets under 64 bytes so the decoder can always use 64-byte wide copies without overlap checks, and fused literals can be copied 4 bytes at a time unconditionally (SPEC.md 'Implementation Notes'). The Go package adds hand-written AMD64 and ARM64 encoder and decoder assembly, hash-table greedy matching at the fast levels, and streams of independent blocks compressed and decompressed on many goroutines (default GOMAXPROCS writers, up to 8 decoders).

## Compared with alternatives

Pick MinLZ over LZ4 when you are in Go, control both ends of the format, and care about compression speed and ratio at the fastest level; keep LZ4 (or lzvolt/ZXC) when decode speed or a C/C++ library is the priority. Over klauspost/compress S2, pick it for a few percent smaller output and faster stream decode at similar compress speed (JSON stream: 3,204 vs 2,378 MiB/s decode).

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | github.com/klauspost/compress (S2/Snappy fallback decoding) |
| **Minimum toolchain** | Go 1.25 per go.mod; README promises support for the two Go releases before the current one |
| **Platforms** | any Go target (pure Go); assembly encoders and decoders on amd64 and arm64; build tags noasm, nounsafe, purego turn off assembly and/or unsafe |
| **Thread safety** | Writers and Readers are per-stream objects (README recommends reusing them across streams); a stream encoder/decoder uses internal goroutines (WriterConcurrency, DecompressConcurrent). Block Encode/Decode are plain functions on caller buffers; concurrent use of one Writer is not documented. |
| **Drop-in for the baseline** | partial — not for LZ4 (different format and language); near drop-in for Go Snappy/S2 users since decoders accept Snappy and S2 content and the API shape matches S2 |

## Gotchas

- Output is not deterministic across builds: assembly and pure-Go encoders 'will often produce slightly different output' (README; issue #12 'Compression output dependent on architecture'), so do not hash compressed bytes for deduplication.
- Block decode needs the exact compressed length; trailing bytes are an error, and blocks carry no checksum.
- Recent fixed issues show the asm/pure-Go paths drift: #68 (closed 2026-09-28) amd64 encodeBlockFast returned buffers to the wrong sync.Pool, so LevelSuperFast reallocated tables every block (allocation cost only, output unaffected); #59 Balanced asm slower than pure Go on incompressible input; #63 pure-Go fast encoders stored a 10-byte repeating pattern uncompressed; #14 Snappy blocks over 8 MB failed to decode via the MinLZ block decoder.
- README block numbers are 16-thread aggregates on cache-hot data; single-stream, single-core speeds are lower and the README explains streams are memory-bandwidth bound.

## Known shortcomings

- Go, not C++. S2 Default is faster than MinLZ level 1 on JSON stream compress. LZ4 level 0 and level 9 show the same 12,649 MB/s, likely a copy error in the README table.
- Go only (go 1.25); the only C port is an experimental CC0 gist, block-only and 'not production level code'. Output differs between asm and pure-Go builds (issue #12). The block API has no checksum. LZ4 decodes faster. README numbers are 16-thread aggregates and the LZ4 binding is not named. Fixed issues, none affecting output correctness: #68 wrong buffer pool, #59 Balanced asm slower than pure Go on incompressible input, #63 pure-Go encoders stored a repeating pattern uncompressed, #14 Snappy blocks over 8 MB failed to decode.

## Caveats and trade-offs

First-party benchmark by the S2/klauspost/compress author's circle; block throughputs use 16 concurrent threads and stream tests use each package's own concurrency, so they are aggregate, not single-core. The non-Go 'LZ4 0' row's implementation is not named, and in the protobuf table 'LZ4 0' and 'LZ4 9' show the same compression speed (12,649 MB/s), which looks like a copy error. On the JSON stream S2 Default compresses faster than MinLZ 1 (15,501 vs 14,921 MiB/s), and LZ4 decompresses blocks faster ('LZ4 is decompression speed king'). Go version and flags are absent.

Go package (C++ would need cgo or a format port); new LZ77 format with a fixed byte-aligned encoding, so streams are not LZ4 compatible; decompression is slower than LZ4 in block tests; MinLZ levels 2-3 trade compress speed for ratio (level 3 compresses at 210 MB/s on the protobuf block).

## Maintenance

Actively maintained by MinIO (v1.2.0, issues fixed through late September 2026), Apache-2.0; usable directly from Go, while C++ users need cgo or the experimental CC0 C block port.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables compare MinLZ with LZ4, Snappy, S2 and gzip on named Snappy testdata and stream corpora on an AMD Ryzen 9 3950X; Go version, flags and the LZ4 implementation are not stated, so C.
- **Verifier notes:** All claimed numbers found in README (protobuf block table and JSON stream table). Metadata: 155 stars, Apache-2.0, not archived, last commit Oct 3, 2026.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** first-party benchmark
- **Pages the verifier opened:**
  - <https://github.com/minio/minlz>
  - <https://github.com/minio/minlz/commits>
  - <https://raw.githubusercontent.com/minio/minlz/HEAD/README.md>
  - <https://raw.githubusercontent.com/minio/minlz/HEAD/LICENSE>
- **Sources the enricher read:**
  - <https://github.com/minio/minlz>
  - <https://raw.githubusercontent.com/minio/minlz/HEAD/README.md>
  - <https://raw.githubusercontent.com/minio/minlz/HEAD/SPEC.md>
  - <https://raw.githubusercontent.com/minio/minlz/HEAD/go.mod>
  - <https://github.com/minio/minlz/issues?q=is%3Aissue>
  - <https://github.com/minio/minlz/issues/68>
  - <https://github.com/minio/minlz/issues/14>
  - <https://gist.github.com/klauspost/5796a5aa116a15eb7341ffa8427bbe7a>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/minio/minlz`) · [data/wave9/enrich/raw/github_com_minio_minlz.json](../../../data/wave9/enrich/raw/github_com_minio_minlz.json) (enrichment confidence 0.8)

</details>
