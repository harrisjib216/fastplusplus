# Rapidgzip

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Compression and encoding](../README.md) › [General-purpose lossless compression](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C++` · `Apache-2.0 AND MIT (repo page lists both; per-file split not checked)` · 🟢 active

> Parallel decompressor and random-access reader for ordinary gzip files; 7-20x faster than GNU gzip on 12 cores.

| | |
|---|---|
| **Beats** | GNU gzip (single-threaded deflate decoder); also compared with pigz, igzip (ISA-L), bgzip and pzstd |
| **Claimed result** | Ryzen 3900X, 20x-silesia with existing index: 5640 MB/s (0 threads=auto) vs gzip 293 MB/s (18.8x); from scratch 2070 MB/s (6.9x); 4GiB-base64 from scratch 5060 MB/s vs gzip 250 MB/s (20.1x). README: up to 24 GB/s with index and 12 GB/s without on 128 cores; 24.3 GB/s vs 9.5 GB/s for pzstd with index. Paper abstract: 5.6 GB/s on Silesia, speedup 33 over GNU gzip, with 128 cores. README: single-core decompression close to igzip and about twice as fast as bgzip (zlib). |
| **Workload** | Decompression of arbitrary gzip files (Silesia tar repeated 20x, 3.95 GiB; 4 GiB base64 data) on a Ryzen 3900X, plus scaling to 128 cores on 2x EPYC 7702. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 3900X (12 cores); 2x AMD EPYC 7702 (2x64 cores) |
| **Adoption** | 469 stars; on PyPI as rapidgzip |
| **Last commit** | 2025-11-30 |
| **Links** | [repository](https://github.com/mxmlnkn/rapidgzip) · [benchmark](https://github.com/mxmlnkn/rapidgzip/blob/master/README.md) |

## Verdict

On a 12-core Ryzen 3900X (compiler and flags not stated), rapidgzip with automatic thread count decompressed 3.95 GiB of 20x-concatenated Silesia at 2070 MB/s from scratch and 5640 MB/s with an index, against 293 MB/s for single-threaded GNU gzip (6.9x and 18.8x). The peer-reviewed HPDC 2023 paper (v0.5.0, 2x EPYC 7702, 128 cores) reports 5.6 GB/s on Silesia (33x over GNU gzip) and 8.7 GB/s on base64 data (55x over gzip); the gain is parallel scaling, not a faster single-thread inflate.

## Use it when

- Large (hundreds of MB and up) .gz files produced by GNU gzip, igzip or pigz that you must read on a machine with 8+ cores: README Ryzen 3900X numbers are 2070 MB/s vs gzip 293 MB/s on 20x Silesia and 5060 vs 250 MB/s on base64 data, from scratch.
- Repeated reads or random access into the same gzip file: export an index once, then decompression reaches 5640 MB/s on the 3900X and up to 24 GB/s on 2x EPYC 7702, and seeks land in a chunk instead of rescanning from the start.
- Genomics and log pipelines in Python that currently use the gzip module or indexed_gzip and are CPU-bound on decompression.
- Mounting .tar.gz archives with ratarmount (rapidgzip is its default gzip backend) for random file access.
- Counting decompressed size or lines in huge gzip files (--count, --count-lines), which can skip decompression entirely when a gztool index with lines exists.

## Skip it when

- Single-threaded or small-file decompression: in the HPDC paper (v0.5.0) one rapidgzip thread reached 153-169 MB/s, about half of igzip; later versions are described as close to igzip, so libdeflate, ISA-L or zlib-ng are the better choice for one core.
- Memory-constrained hosts: without an index each thread holds chunks whose size scales with the compression ratio (paper: about 80 MiB per thread at ratio 10, worst case 8.3 GiB per thread at ratio 1032 before the current 20x-chunk cap); the cache holds twice as many chunks as threads, and issue #69 reports 8 GB not released by RapidgzipFile after an index export (open).
- Files that are effectively one Deflate block (igzip -0) or only Fixed-Huffman blocks: the block finder cannot split them, so decompression stays serial.
- Integrity checks on possibly truncated input: issue #71 (open, v0.16.0, 2026-08-31) shows exit status 0 for some gzip files truncated mid-Deflate-stream, depending on truncation point and -P setting; GNU gzip reports an error.
- Highly redundant data (FASTQ, Silesia-like text) on many-socket machines without an index: the sequential marker resolution of the last 32 KiB per chunk caps scaling around 64 cores (paper and README FASTQ plot).

## How it is fast

It generalizes pugz's two-stage scheme: worker threads start inside the file at Deflate block candidates found by a fast block finder (skip-table checks of Dynamic and Non-Compressed block headers), decode with the unknown 32 KiB window filled by 15-bit marker symbols, and the markers are resolved once the preceding chunk's window is known. A cache keyed by chunk offset plus a parallel prefetcher make it robust to false-positive block offsets, which simply get evicted. With an index (windows known) it skips marker resolution and hands chunks to ISA-L or zlib-ng, which is why indexed decompression is 2-3x faster on Silesia-like data.

## Compared with alternatives

Pick rapidgzip over ISA-L igzip, libdeflate, zlib-ng or Wuffs when you have one large existing .gz file and many idle cores, or need random access into it; those siblings are faster per core and simpler to embed but decode a single gzip stream on one thread. Against zstd it is the option when you cannot re-compress the data: README reports 24.3 GB/s vs 9.5 GB/s for pzstd with an index on 128 cores.

## Integration

| | |
|---|---|
| **Form** | header-only C++ library (via CMake add_subdirectory/FetchContent of librapidarchive), plus CLI and PyPI wheel |
| **Dependencies** | Optional but on by default: ISA-L (needs nasm on x86-64), zlib-ng (or zlib/system zlib), rpmalloc; cxxopts for the CLI |
| **Minimum toolchain** | C++17, CMake 3.17+ |
| **Platforms** | Linux, Windows, macOS (PyPI wheels); x86-64 and aarch64 with ISA-L; RISC-V 64 builds without rpmalloc; ISA-L is disabled on macOS in the CMake build |
| **Thread safety** | ParallelGzipReader is internally multithreaded but its methods are documented as not thread-safe; use one reader per calling thread. |
| **Drop-in for the baseline** | partial — the CLI accepts gzip-style -d/-c/-k/-f flags and works with tar --use-compress-program, and RapidgzipFile mirrors Python's gzip file object, but the C++ API is its own reader class, not a zlib inflate() replacement, and it cannot compress. |

## Gotchas

- Without -f, output piped to /dev/null may skip the actual decoding, so naive benchmarks overstate speed.
- CRC32 verification is controllable (--verify/--no-verify); turning it off speeds things up but relies on implicit checks.
- The first seek on a file without an index builds the whole block-offset map, so it can take as long as a full decompression; export and import the index to avoid this.
- Development happens in mxmlnkn/indexed_bzip2 (librapidarchive); the rapidgzip repo is a release mirror, while issues go to the rapidgzip repo.

## Known shortcomings

- Tier B on the HPDC 2023 paper (read via the indexed_bzip2 repo PDF): 5.6 GB/s on Silesia, 33x over GNU gzip on many cores, but single-thread it is 153 MB/s and bgzip (1.9x) and igzip (4.3x) are faster per thread; no compiler or flags.
- Open #71 (v0.16.0): exits 0 on some gzip files truncated mid-Deflate; open #69: RapidgzipFile holds 8 GB of RAM after index export; the paper gives up to 8.3 GiB per thread at the worst-case ratio. Single-thread it is about half igzip (paper, v0.5.0). License split undocumented (README, LICENSE-MIT and CITATION.cff say MIT, LICENSE-APACHE also present); ISA-L is off on macOS.

## Caveats and trade-offs

Peer-reviewed (ACM HPDC 2023, DOI 10.1145/3588195.3592992); the paper PDF in mxmlnkn/indexed_bzip2/results/paper was opened, but neither it nor the README states the compiler or flags. The headline gain is parallel scaling versus single-threaded GNU gzip, not a faster single-thread inflate: in the paper (rapidgzip 0.5.0), single-threaded rapidgzip reached 153 MB/s, while bgzip was 1.9x and igzip 4.3x as fast; the README's claim that single-core speed is close to igzip refers to later versions. Baseline is GNU gzip rather than zlib. The README scaling plots used rapidgzip 0.9.0, and its values are higher than the paper's. The paper's text gives GNU gzip on Silesia as "172 GB/s", an evident typo for MB/s.

Multi-core only wins: single-thread speed is close to igzip, not faster. Needs memory for chunk cache and a two-stage decode of unknown windows; with an index it reaches higher bandwidth. Read-only decompressor (compression is delegated to other tools). C++17, usable as header-only C++ library.

## Maintenance

Active (v0.16.0 on 2025-11-30, development continuing in indexed_bzip2) and permissively licensed (MIT per README, LICENSE-MIT and CITATION.cff; the repo also carries LICENSE-APACHE without a documented split), with two open correctness/memory issues (#71, #69) worth checking before production use.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification B, tier now B.
- **Tier reason:** A peer-reviewed ACM HPDC 2023 paper (opened as the PDF checked into mxmlnkn/indexed_bzip2) reports 5.6 GB/s on Silesia, a speedup of 33 over GNU gzip, and 8.7 GB/s on base64 data, a speedup of 55 over gzip and 21 over igzip, on 2x AMD EPYC 7702. Neither the paper nor the README states the compiler or flags, so not A.
- **Verifier notes:** README Ryzen 3900X tables match the record exactly (5640 MB/s vs gzip 293 MB/s, 18.8x with index; 2070 MB/s, 6.9x from scratch; base64 5060 vs 250 MB/s, 20.1x). Last commit 2025-11-30 (v0.16.0), within 12 months, so active. The repo page lists Apache-2.0 and MIT; the per-file split was not checked.
- **Fields the verifier corrected:** `caveats`
- **Shortcomings recorded by:** verifier read the HPDC 2023 PDF; enricher
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/mxmlnkn/rapidgzip/HEAD/README.md>
  - <https://raw.githubusercontent.com/mxmlnkn/indexed_bzip2/master/results/paper/Knespel%2C%20Brunst%20-%202023%20-%20Rapidgzip%20-%20Parallel%20Decompression%20and%20Seeking%20in%20Gzip%20Files%20Using%20Cache%20Prefetching.pdf>
  - <https://github.com/mxmlnkn/rapidgzip>
  - <https://github.com/mxmlnkn/rapidgzip/commits>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/mxmlnkn/rapidgzip/HEAD/README.md>
  - <https://github.com/mxmlnkn/rapidgzip>
  - <https://raw.githubusercontent.com/mxmlnkn/rapidgzip/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/mxmlnkn/rapidgzip/HEAD/.gitmodules>
  - <https://raw.githubusercontent.com/mxmlnkn/rapidgzip/HEAD/LICENSE-MIT>
  - <https://raw.githubusercontent.com/mxmlnkn/rapidgzip/HEAD/LICENSE-APACHE>
  - <https://raw.githubusercontent.com/mxmlnkn/rapidgzip/HEAD/CITATION.cff>
  - <https://raw.githubusercontent.com/mxmlnkn/indexed_bzip2/master/CMakeLists.txt>
  - <https://raw.githubusercontent.com/mxmlnkn/indexed_bzip2/master/src/rapidgzip/ParallelGzipReader.hpp>
  - <https://raw.githubusercontent.com/mxmlnkn/indexed_bzip2/master/results/paper/Knespel%2C%20Brunst%20-%202023%20-%20Rapidgzip%20-%20Parallel%20Decompression%20and%20Seeking%20in%20Gzip%20Files%20Using%20Cache%20Prefetching.pdf>
  - <https://github.com/mxmlnkn/rapidgzip/issues?q=is%3Aissue>
  - <https://github.com/mxmlnkn/rapidgzip/issues/71>
  - <https://github.com/mxmlnkn/rapidgzip/issues/69>
- **Raw records:** [data/wave9/verified.json](../../../data/wave9/verified.json) (id `https://github.com/mxmlnkn/rapidgzip`) · [data/wave9/enrich/raw/github_com_mxmlnkn_rapidgzip.json](../../../data/wave9/enrich/raw/github_com_mxmlnkn_rapidgzip.json) (enrichment confidence 0.85)

</details>
