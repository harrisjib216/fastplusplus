# rust-linereader

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Runtime and systems](../README.md) › [Filesystems and I/O](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🔴 abandoned

> Small Rust buffered reader returning borrowed line slices; beats std BufRead::read_until and lines() for byte-oriented line scanning.

| | |
|---|---|
| **Beats** | Rust std BufRead::read_until / read_line / lines |
| **Claimed result** | next_batch 0.27 s (38.3M lines/s) vs read_until 1.94 s (5.3M lines/s), read_line 2.54 s, lines() 3.23 s; like-for-like per-line next_line 1.51 s vs read_until 1.94 s (1.28x, derived from page data). Raw read() with no line splitting is 0.25 s. |
| **Workload** | Read a 976MB, 10.3M line file on a Westmere Xeon 2.1GHz, FreeBSD/ZFS |
| **Metric** | throughput |
| **Hardware** | Westmere Xeon 2.1GHz, FreeBSD/ZFS |
| **Adoption** | 26 stars |
| **Last commit** | 2019-09-13 |
| **Links** | [repository](https://github.com/Freaky/rust-linereader) · [benchmark](https://github.com/Freaky/rust-linereader) |

## Verdict

The author's README run on a 976 MB, 10.3M-line XML file (Westmere Xeon 2.1 GHz, FreeBSD/ZFS, compiler and harness not published) measured next_batch 0.27 s vs raw read() 0.25 s, next_line 1.51 s, std read_until 1.94 s, read_line 2.54 s and lines() 3.23 s; a second run recorded in src/lib.rs on a 31.6 GB, 501.6M-line input gave LineReader 407.52 MB/s vs read_until 252.62 MB/s (1.61x, derived from page data). The std BufReader capacity used for the baselines is not stated, versus LineReader's 64 KiB buffer.

## Use it when

- Scanning large log or text files line by line as bytes (no UTF-8 validation needed) where read_until plus buf.clear() is the hot loop
- Pipelines that can process many lines at once: next_batch() hands out multi-line blocks for your own memchr/SIMD parsing or for passing to worker threads
- Inputs with a known maximum line length that fits comfortably within the buffer (configure with with_capacity)
- Non-newline record separators such as NUL or tab via with_delimiter

## Skip it when

- Inputs with unbounded line length: lines longer than the buffer are silently split and you cannot tell a truncated line from a final line without a newline (open issue #3)
- Code that needs owned Strings or UTF-8 validated lines: you must copy and validate yourself, which erodes the per-line gain
- New projects that want maintained code: unmaintained since 2019 (v0.4.0); the author points to bstr for_byte_line (0.2.8+) as performing similarly without the line-length limit
- Expecting the 7x headline per line: like-for-like next_line() was 1.51 s vs read_until 1.94 s (1.28x) on the README run

## How it is fast

It avoids per-line copying and allocation by borrowing from a fixed buffer, and finds delimiters with the memchr crate (memchr for the next line, memrchr to find the last complete line after each read). next_batch() skips per-line splitting entirely, so a caller with its own SIMD or parallel scanner gets whole blocks of complete lines at near raw read() speed; refill only moves the trailing partial line to the buffer start.

## Compared with alternatives

rawscan is the closest sibling (C, beats fgets/getline on CPU time); pick linereader inside Rust code for byte-line scanning, and rawscan for C/C++ programs. For a maintained Rust option compare against bstr's for_byte_line before adopting this.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | memchr 2 |
| **Minimum toolchain** | not documented (Rust 2015 edition, extern crate syntax) |
| **Platforms** | any |
| **Thread safety** | Single reader object with &mut self methods; returned slices borrow the reader, so it is not shared across threads (issue #1 on thread-friendly batching still open) |
| **Drop-in for the baseline** | no |

## Gotchas

- Returned slices borrow the reader's buffer and are invalidated by the next call, so collecting lines requires to_vec()
- Lines longer than the buffer come back as several pieces, and the only hint is the missing trailing delimiter
- Using get_mut() on the inner reader without reset() desynchronizes buffered state
- When the leftover fragment is longer than the consumed part, refill uses Vec::drain plus extend with a fresh zeroed Vec, an allocation on that path

## Known shortcomings

- Rust, not C++. The baselines' BufReader capacity is not stated while LineReader uses 64 KiB. Issue 3 is open: a truncated line looks the same as a last line without a newline. A second run in a src/lib.rs comment gives 407.52 vs 252.62 MB/s against read_until (1.61x, derived).

## Caveats and trade-offs

Baseline is the Rust standard library BufRead, not POSIX read. next_batch returns a slice of all complete lines in the buffer, so its 7x over read_until is not a per-line comparison; the per-line next_line gain is about 1.28x. Lines longer than the buffer are split. No benchmark harness or flags published. Abandoned since 2019; author notes bstr 0.2.8+ for_byte_line should perform similarly.

Line length limited by buffer size; author says bstr for_byte_line performs similarly without that limit.

## Maintenance

Abandoned since 2019-09-13 (v0.4.0 on crates.io, about 2.0M downloads, about 289k recent), but MIT-licensed, about 400 lines with no unsafe code and a single memchr dependency, so it is easy to vendor.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** README Performance table (author's own run on Westmere Xeon 2.1GHz, FreeBSD/ZFS) compares LineReader with std read_until/read_line/lines; no benchmark code path, compiler version or flags stated, so C.
- **Verifier notes:** Numbers match README. Claim corrected to flag the batch-vs-line apples-to-oranges comparison. MIT, 26 stars, last commit 2019-09-13 confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** code reading by enricher
- **Pages the verifier opened:**
  - <https://github.com/Freaky/rust-linereader>
  - <https://github.com/Freaky/rust-linereader/commits>
  - <https://raw.githubusercontent.com/Freaky/rust-linereader/HEAD/README.md>
- **Sources the enricher read:**
  - <https://github.com/Freaky/rust-linereader>
  - <https://raw.githubusercontent.com/Freaky/rust-linereader/HEAD/README.md>
  - <https://raw.githubusercontent.com/Freaky/rust-linereader/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/Freaky/rust-linereader/HEAD/src/lib.rs>
  - <https://crates.io/api/v1/crates/linereader>
  - <https://github.com/Freaky/rust-linereader/issues?q=is%3Aissue>
- **Raw records:** [data/wave11/verified.json](../../../data/wave11/verified.json) (id `https://github.com/freaky/rust-linereader`) · [data/wave11/enrich/raw/github_com_freaky_rust_linereader.json](../../../data/wave11/enrich/raw/github_com_freaky_rust_linereader.json) (enrichment confidence 0.75)

</details>
