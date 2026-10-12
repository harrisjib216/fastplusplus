# evtx (Rust Windows Event Log parser and evtx_dump)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust Windows .evtx parser and evtx_dump CLI; 8.8x faster than libyal's C evtxexport on one thread (same run).

| | |
|---|---|
| **Beats** | libevtx evtxexport (C, libyal), built from source by the repo's benchmark script |
| **Claimed result** | README (June 2026, evtx 0.12.2 PGO build, bench commit 99a6def), 30 MB security_big_sample.evtx to XML: evtx 71.6 ms on 1 thread, 20.7 ms on 8 threads vs libevtx (C) 2.439 s as printed (about 34x and 118x), but the libevtx figure was carried over from January 2026 while the evtx columns were re-measured in June (cross-run); the same-run comparison is about 8.8x (derived from page data). |
| **Workload** | Convert a 30 MB Windows Security event log (samples/security_big_sample.evtx) to XML text written to /dev/null; wall-clock time measured with hyperfine (warmup 2, 5 runs by default in the script). |
| **Metric** | throughput |
| **Hardware** | 12-core AMD Ryzen 3900X, Arch Linux; evtx columns measured June 2026 on Linux 7.0.11-arch1-1 (bench commit 99a6def), libevtx figure from the January 2026 run on Linux 6.17.9-arch1-1 (bench commit e01782a); hyperfine, 2 warmups and 5 runs by script default. |
| **Compiler and flags** | evtx: Cargo release profile opt-level 3, codegen-units 1, lto thin; README numbers come from build_pgo.sh (RUSTFLAGS -Cprofile-generate then -Cprofile-use, features fast-alloc (tikv-jemallocator) and wevt_templates); rustc version not stated. The committed bench script itself builds a plain 'cargo build --release --bin evtx_dump' without fast-alloc or PGO (README says PGO is worth 2-5%). libevtx: scripts/bench_all_parsers.sh clones libyal/libevtx at HEAD (unpinned), runs synclibs.sh/autogen.sh, './configure --enable-static --disable-shared --enable-static-executables' and make with no CFLAGS (autoconf default, normally -g -O2); C compiler and version not stated. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | no |
| **Why it wins** | README credits a compiled-template rewrite (docs/compiled-templates.html, not opened), PGO and, for the 8-thread column, parallel chunk parsing. The one-thread gap over libevtx has no stated mechanism. |
| **Adoption** | 966 stars, 86 forks; evtx crate 310,212 downloads on crates.io (latest 0.12.3, 2026-09-22); PyPI wheel via pyevtx-rs |
| **Last commit** | 2026-10-07 |
| **Links** | [repository](https://github.com/omerbenamram/evtx) · [benchmark](https://raw.githubusercontent.com/omerbenamram/EVTX/HEAD/README.md) |

## Verdict

On a 12-core Ryzen 3900X (Arch Linux, hyperfine, 2 warmups, 5 runs), converting the 30 MB, 62,000-record security_big_sample.evtx to XML on /dev/null took 275.9 ms with evtx on one thread and 79.5 ms on 24 threads, against 2.439 s for libevtx's evtxexport -f xml in the same January 2026 run (8.8x and 31x). The current README's 71.6 ms (1 thread) and 20.7 ms (8 threads) come from the June 2026 PGO and jemalloc build and are compared with that January libevtx figure, so 34x and 118x are cross-run ratios. Compiler versions are not stated for either side.

## Use it when

- Bulk conversion of large .evtx files (tens of MB to GB) to JSON Lines or XML for SIEM ingestion, DFIR timelines or DuckDB/jq analysis, where libevtx's evtxexport takes seconds per 30 MB file.
- You want JSON directly: evtxexport writes only text or XML, while evtx renders JSON from the same compiled templates without an XML-to-JSON step.
- Multi-core machines processing one big log: chunks parse in parallel (README: 20.7 ms at 8 threads vs 71.6 ms on one thread for the 30 MB sample), with chunk order preserved by the pipeline.
- Rust, Python (pyevtx-rs wheel) or browser (WASM viewer) codebases that need an embeddable parser with no C toolchain.
- Damaged or dirty logs: it keeps reading past the header's chunk count and has basic record and chunk recovery.

## Skip it when

- You need output that matches evtxexport or Windows Event Viewer byte for byte: the XML layout differs (evtx_dump prints 'Record N' lines unless told not to), and no equivalence check against libevtx exists.
- Logs that use CDATA or EVTHandle nodes, which README lists as unimplemented.
- Forensic work that needs every typed value preserved: open issue #289 reports that BoolType fields holding values other than 0 or 1 (for example a 320060673 NTFS attribute mask) are silently turned into true, and the maintainer reply did not settle a fix.
- C or C++ projects that want a linkable library: evtx has no C ABI; libevtx and its Python bindings remain the C option.
- Pipelines that rely on chunk CRC checks: evtx skips checksum validation by default (--validate-checksums is opt-in), while libevtx always computes both chunk CRC-32 values and flags corrupt chunks.

## How it is fast

Since 0.12.2 (June 2026) each binary-XML template is compiled once per file into a constant text buffer and a short list of fill-in instructions (copy literal range, format value N, run a nested template), shared across worker threads through a content-keyed cache. Each record then formats its raw value bytes straight into the output with fused SIMD UTF-16-to-UTF-8 escaping (SSE2 or NEON), with no per-record tree or value enum. libevtx, by contrast, builds a libfwevt XML document for every record and then serialises it twice (a size pass, then a copy pass). Chunks are rendered in parallel on a rayon pipeline into bumpalo arenas and written with one write_all per chunk; release builds add thin LTO, codegen-units 1, optional jemalloc and PGO.

## Compared with alternatives

No other EVTX parser is catalogued; among the format-parser siblings (mail-parser for MIME, PDFOxide for PDF text, YARA-X for rule scanning) pick evtx whenever the input is a Windows .evtx log, and treat its speedup as the same kind of design win as mail-parser's rather than a Rust-versus-C result.

## Integration

| | |
|---|---|
| **Form** | crate (also evtx_dump binary, PyPI wheel via pyevtx-rs, WASM build) |
| **Dependencies** | bitflags, crc32fast, byteorder, thiserror, log, winstructs, ahash, serde, serde_json, sonic-rs, zmij, jiff, bumpalo, in-repo utf16-simd, an ANSI codec crate (encoding in 0.12.3, encoding_rs on master); optional rayon (default 'multithreading'), clap/anyhow/simplelog/dialoguer/indoc/tempfile (default 'evtx_dump'), goblin and glob ('wevt_templates'), tikv-jemallocator or rpmalloc ('fast-alloc') |
| **Minimum toolchain** | Rust edition 2024, so Rust 1.85 or newer; no rust-version is declared in Cargo.toml or on crates.io |
| **Platforms** | any Rust target with std; SIMD UTF-16 fast path on x86-64 (SSE2, runtime detected) and aarch64 (NEON), scalar elsewhere; release binaries for 64-bit Windows, macOS and Linux |
| **Thread safety** | Parallelism is internal: ParserSettings::num_threads (0 = rayon's thread count) runs chunks on a bounded rayon pipeline that yields chunks in order; the iterators borrow the parser mutably, so one parser serves one consumer. Sharing a parser across threads is not documented. |
| **Drop-in for the baseline** | partial — replaces evtxexport for converting .evtx to XML (and adds JSON), but with a different CLI, a different XML layout, no C API, and CDATA/EVTHandle nodes unimplemented |

## Gotchas

- Benchmark harness: the README's headline 34x (1 thread) and 118x (8 threads) pair a June 2026 evtx run with a libevtx figure (2.439 s) carried over unchanged from the January 2026 run on another kernel; only the January run is same-run (275.9 ms vs 2.439 s, 8.8x). The README figures come from the PGO plus fast-alloc (jemalloc) binary, but scripts/bench_all_parsers.sh builds a plain 'cargo build --release' and libevtx at an unpinned HEAD (configure.ac is now version 20261009) with autoconf default flags, so the committed script does not reproduce either side of the table. build_pgo.sh trains on every file in samples/, which includes the benchmark input security_big_sample.evtx (README puts PGO at 2-5%).
- Work is not identical: libevtx computes two CRC-32 checksums per chunk on every run, evtx skips checksum validation unless --validate-checksums is passed. On the 2.4 s baseline this is small, but it is extra work only the C side does.
- README and docs/compiled-templates.html say the crate is 100% safe Rust 'including the SIMD UTF-16 conversion'; the evtx crate root does carry #![forbid(unsafe_code)], but the in-repo utf16-simd dependency that does the SIMD escaping uses raw pointers, Vec::set_len on MaybeUninit buffers and SSE2/NEON intrinsics (42 'unsafe' occurrences in simd.rs), and sonic-rs is also unsafe internally.
- README still warns that multithreaded evtx_dump may print records out of order; the 0.12 chunk pipeline reorders completed chunks (BTreeMap keyed by sequence) before yielding, so that note looks stale. The compiled-templates write-up calls the release 'v0.13' while it shipped as 0.12.2.

## Known shortcomings

- The README 34x/118x pair a June 2026 evtx run with a libevtx time carried over from January 2026 (cross-run); the only same-run comparison (January README b2f4cba) is 275.9 ms vs 2.439 s, 8.8x on one thread; no compiler versions; libevtx built from unpinned HEAD at autoconf default flags (likely -g -O2) while evtx has PGO, thin LTO and jemalloc; no check that both emit equivalent XML.
- The README's 34x/118x pair a June 2026 evtx run with a January libevtx 2.439 s (cross-run); the same-run figure is 8.8x. The committed bench script does not rebuild the README binary (PGO plus jemalloc vs plain release; libevtx unpinned HEAD, now 20261009), and build_pgo.sh trains on samples/, which include the benchmark input security_big_sample.evtx. Work asymmetry: libevtx always computes 2 CRC-32s per chunk while evtx skips them unless --validate-checksums. The '100% safe Rust' claim is overstated (the in-repo utf16-simd has 42 unsafe blocks in simd.rs); open #289: non-0/1 bool values silently become true; the README out-of-order note is stale (the 0.12 pipeline reorders chunks).

## Caveats and trade-offs

Category fit is weak: the input is a binary log format (binary XML templates) and the output is XML text. The headline 34x/118x ratios in the current README are cross-run: the evtx columns were re-measured in June 2026 after the compiled-template rewrite while the libevtx 2.439 s figure was carried over from January 2026 (different kernel); the only same-run comparison is January 2026 (8.8x single-threaded, 31x at 24 threads). Optimisation levels are not matched: evtx uses opt-level 3, thin LTO, codegen-units 1, PGO and jemalloc, libevtx is a stock autoconf build (likely -g -O2, no LTO or PGO) at an unpinned HEAD. The committed bench script does not reproduce the PGO/jemalloc binary the README measured. No check that evtxexport -f xml and evtx_dump emit equivalent XML. The multi-thread columns compare a parallel program against single-threaded evtxexport. First-party, one machine, one input file, compiler versions absent. The speed-up is a design win (per-template compiled output, SIMD UTF-16 escaping, arena allocation), not a language-level one. [retier] The committed bench script does not rebuild the README binary (PGO plus jemalloc vs plain release; libevtx unpinned HEAD), and build_pgo.sh trains on samples/, which include the benchmark input. libevtx always computes 2 CRC-32s per chunk while evtx skips them unless --validate-checksums. The '100% safe Rust' claim is overstated (utf16-simd has 42 unsafe blocks); open #289: non-0/1 bool values silently become true.

Read-only parser; CDATA nodes and EVTHandle nodes are unimplemented. Safe Rust with optional multithreading. Outputs XML or JSON.

## Maintenance

Actively maintained (last commit 2026-10-07, 0.12.3 released 2026-09-22, about 311,000 crates.io downloads), dual MIT/Apache-2.0, with an unreleased breaking change on master that swaps the ANSI codec type to encoding_rs; copyable as a crate or prebuilt binary.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification A, tier now C.
- **Tier reason:** First-party hyperfine numbers with public harness code (scripts/bench_all_parsers.sh) and a named CPU (Ryzen 3900X), but no compiler versions for either side, libevtx is cloned at an unpinned HEAD and built with no explicit CFLAGS, and the current README's libevtx figure is carried over from a January 2026 run while the evtx columns were re-measured in June 2026, so the headline 34x is a cross-run ratio; not A.
- **Verifier notes:** Downgrade A to C: no compiler versions, unpinned libevtx built at autoconf default flags, and the current README's 34x pairs a June 2026 evtx run with a January 2026 libevtx run; use the January same-run 8.8x (1 thread) as the solid figure. Shortcomings: cross-run headline ratio, unmatched opt levels (PGO+LTO+jemalloc vs default -O2), no output-equivalence check, parallel vs single-threaded columns, weak string-and-text fit.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `hardware`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-103 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/README.md>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/scripts/bench_all_parsers.sh>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/build_pgo.sh>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/docs/compiled-templates.html>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/b2f4cba/README.md>
  - <https://github.com/omerbenamram/evtx>
  - <https://github.com/omerbenamram/evtx/commits/master>
  - <https://github.com/omerbenamram/evtx/commits/master/README.md>
  - <https://crates.io/api/v1/crates/evtx>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/README.md>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/scripts/bench_all_parsers.sh>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/build_pgo.sh>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/docs/compiled-templates.html>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/src/evtx_parser.rs>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/src/bin/evtx_dump.rs>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/utf16-simd/Cargo.toml>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/utf16-simd/src/lib.rs>
  - <https://raw.githubusercontent.com/omerbenamram/evtx/HEAD/utf16-simd/src/simd.rs>
  - <https://raw.githubusercontent.com/libyal/libevtx/main/evtxtools/evtxexport.c>
  - <https://raw.githubusercontent.com/libyal/libevtx/main/evtxtools/export_handle.c>
  - <https://raw.githubusercontent.com/libyal/libevtx/main/libevtx/libevtx_record.c>
  - <https://raw.githubusercontent.com/libyal/libevtx/main/libevtx/libevtx_record_values.c>
  - <https://raw.githubusercontent.com/libyal/libevtx/main/libevtx/libevtx_chunk.c>
  - <https://raw.githubusercontent.com/libyal/libevtx/main/configure.ac>
  - <https://github.com/omerbenamram/evtx>
  - <https://github.com/omerbenamram/evtx/commits/master>
  - <https://github.com/omerbenamram/evtx/issues>
  - <https://github.com/omerbenamram/evtx/issues/289>
  - <https://crates.io/api/v1/crates/evtx>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/omerbenamram/evtx`) · [data/wave14/enrich/raw/github_com_omerbenamram_evtx.json](../../../data/wave14/enrich/raw/github_com_omerbenamram_evtx.json) (enrichment confidence 0.8)

</details>
