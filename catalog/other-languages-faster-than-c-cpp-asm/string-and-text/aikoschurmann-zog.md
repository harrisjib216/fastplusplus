# zog (Zig SIMD JSONL search)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig CLI that filters, extracts and aggregates JSONL by raw byte scanning; README claims 20-50x over jq/jaq.

| | |
|---|---|
| **Beats** | jq (C); the README row is labelled 'jq/jaq' so it is not clear which of the two produced each number; ripgrep (Rust) is also compared |
| **Claimed result** | README: '20-50x faster than jq/jaq for typical queries', '4.1x faster than ripgrep for complex multi-condition logic', aggregations '40x faster than jq'. Table, GB/s zog(file) / zog(pipe) / ripgrep / jq-jaq: simple key match 4.03 / 2.38 / 2.30 / 0.07; substring match (HAS) 2.49 / 2.09 / 1.53 / 0.07; numeric comparison 3.39 / 2.41 / 2.97 / 0.10; field extraction (TSV) 2.83 / 2.21 / N/A / 0.10; JSON re-formatting 2.77 / 2.18 / N/A / 0.10; aggregations 2.41 / 1.91 / N/A / 0.05; complex logic (OR/AND) 2.24 / 1.93 / 0.54 / 0.06. Ratios against jq/jaq: about 28-58x in file mode and 22-38x in pipe mode (derived from page data). |
| **Workload** | Search, filter, extract, re-format and aggregate over a 1 GB JSONL file with 6.7 million lines; GB/s per workload, zog reading a file (background reader thread with 8 MB double buffering) or a pipe. Whether the file was in the page cache, the dataset's shape and the exact queries and baseline command lines are not given. |
| **Metric** | throughput |
| **Hardware** | Only 'a modern NVMe SSD' is named; no CPU model |
| **Compiler and flags** | Build instructions say 'zig build -Doptimize=ReleaseFast' (build.zig falls back to Debug without the flag); the build mode, Zig version and flags of the benchmarked binary, and the versions and builds of jq, jaq and ripgrep, are not stated. The repo migrated from Zig 0.13.0 to 0.16.0 on 2026-07-02, so the README numbers may predate that. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | Repository description: zero-allocation JSONL search engine using SIMD (field matching without building a DOM); jq parses every line into a full value tree. Mechanism is from the repo description, not from a profile. |
| **Adoption** | 49 stars |
| **Last commit** | 2026-07-17 |
| **Links** | [repository](https://github.com/aikoschurmann/zog) · [benchmark](https://github.com/aikoschurmann/zog) |

## Verdict

Only the author's README table backs the claim, unchanged since commit 7e83065 (2026-02-27, the Zig 0.13 code): a 1 GB, 6.7-million-line JSONL file on 'a modern NVMe SSD', with no CPU, versions, flags, commands, dataset or cache state given. zog file mode ran at 2.24-4.03 GB/s versus 0.05-0.10 GB/s for a merged jq/jaq column (about 28-58x, derived from page data). ripgrep ran at 0.54-2.97 GB/s on the three rows it can express, and zog's file mode uses two threads.

## Use it when

- Grepping large flat JSONL logs (one object per line, few nested keys) for a field value or range at multi-GB/s, where jq's full parse is the bottleneck.
- Quick COUNT/SUM/MIN/MAX/AVG over a field in a single pass, when approximate semantics (string "99.99" counted as a number) are acceptable.
- Pre-filtering a big file down to candidate lines before handing them to jq, jaq or Miller for exact processing.
- Streaming use (tail -f app.jsonl | zog level eq error) on Linux x86-64 or macOS arm64, where prebuilt binaries exist.

## Skip it when

- Any query where nesting matters: a key inside a sub-object, an array element or even a string value equal to the key name is treated as the key (see gotchas).
- Producing JSON for another program: --format json can emit invalid or retyped JSON, and object or array values are cut short.
- Numbers written in different forms (eq 90 does not match 90.0), integers of 19 or more digits, keys written with \u escapes, pretty-printed JSON, or lines longer than 8 MiB.
- Anything needing validation, paths, transforms, sorting, grouping or parentheses in boolean logic; use jq, jaq or Miller.
- Windows (no release binary; the v0.1.1 release note says 'windows support later').

## How it is fast

It never parses JSON. A reader thread fills two 8 MiB buffers in turn (cut at the last newline) while the main thread splits lines with 32-byte @Vector newline masks and @ctz, and finds candidate keys by comparing one vector against '"' and the next (offset by one byte) against the key's first character. Each hit is confirmed with memcmp, then the value is compared as raw bytes (pre-quoted string, literal number with a terminator check, or a fast integer/float parse for range operators). The query is compiled once up front, and the scan allocates no heap memory.

## Compared with alternatives

Pick zog over Miller 6 when the data is flat JSONL, the question is a simple field filter or sum, and throughput matters more than exact JSON semantics; Miller parses the JSON properly and handles nesting. If the data can be TSV, eBay tsv-utils (tsv-filter) gives correct field semantics at lower but still fast speeds.

## Integration

| | |
|---|---|
| **Form** | standalone CLI binary (single static executable; prebuilt zog-linux-amd64 and zog-macos-arm64, or zig build -Doptimize=ReleaseFast) |
| **Dependencies** | none (Zig standard library only) |
| **Minimum toolchain** | Zig 0.16.0 (build.zig.zon minimum_zig_version); build.zig defaults to Debug unless -Doptimize is given |
| **Platforms** | Linux x86-64 and macOS arm64 binaries; portable @Vector(32, u8) code. The release workflow builds -Dtarget=x86_64-linux with no -Dcpu, so the Linux binary targets baseline x86-64 and its 32-byte vectors lower to SSE2 rather than the AVX2 the README describes; build with -Dcpu=native for AVX2. |
| **Thread safety** | not applicable (CLI); internally one reader thread plus one scanning thread synchronised with two semaphores |
| **Drop-in for the baseline** | no |

## Gotchas

- The WHERE matcher accepts any occurrence of the quoted key text and does not check for a following colon, so a string value equal to the key name counts. Read from src/scanner.zig: `error exists` matches {"level":"error"}, and because neq succeeds if ANY occurrence differs, `status neq 200` matches {"type":"status","status":200}. Use NOT key eq value for a safe negation.
- --format json decides whether to quote a string by its first byte (isFastPrimitive: a digit, '-', 't', 'f' or 'n'), so the string "fatal" is printed as fatal (invalid JSON) and "45" becomes the number 45. Object and array values are cut at the first comma or closing brace, and keys and values are not escaped. The same code existed at the benchmarked commit 7e83065, so the 'JSON Re-Formatting' row compares output that is not equivalent to jq's (a harness flaw in the comparison, not a measurement error).
- SELECT with one field (including a single aggregate) uses a looser extractor (extractValueSingle, no colon check) than SELECT with two or more fields. If the key name first appears as a string value, the single-field path returns an empty value: `SELECT sum:bytes` can undercount where `SELECT sum:bytes,count:bytes` does not, and `count:error` counts lines that contain the string "error" anywhere.
- parseFastInt accumulates into i64 with no overflow check, so a data integer of 19 or more digits (9.22e18 or more) in a range comparison or an aggregation is undefined behaviour in the ReleaseFast release builds and a panic in Debug or ReleaseSafe. A line longer than the 8 MiB block never fits the buffer, and the reader then issues a zero-length read that ends the scan early (code reading, not tested).

## Known shortcomings

- First-party README table only: no benchmark script, CPU or baseline versions; jq and jaq share one column; zog ignores JSON nesting, matches numbers literally and does no validation, and uses a reader thread against single-threaded jq. Tool-vs-tool comparison (22-58x derived), not Zig-vs-C.
- Correctness bugs in the measured code (src/scanner.zig, present at benchmarked commit 7e83065): --format json leaves strings unquoted when the first byte is a digit, '-', 't', 'f' or 'n' ('fatal' prints as fatal, invalid JSON) and truncates objects and arrays, so the JSON re-formatting row is not equivalent to jq; WHERE matches key text anywhere with no colon check (`error exists` matches {"level":"error"}; neq is true if any occurrence differs); single-field SELECT and aggregates can return an empty value (sum undercounts); unchecked i64 overflow on 19+ digit integers; lines over 8 MiB end the scan. README numbers date from 2026-02-27, before the Zig 0.16 std.Io port (v1.0.0 unmeasured); the Linux release is built for baseline x86-64 (SSE2, not AVX2); README asset name zog-linux-x64 is wrong (real: zog-linux-amd64).

## Caveats and trade-offs

First-party only: no CPU, no benchmark script or dataset in the repository, no baseline versions or flags, and jq and jaq are merged into one column. zog does different and weaker work than jq: it does not parse or validate JSON, ignores nesting (a key inside a sub-object matches as if it were a root key), matches numbers literally (90 does not equal 90.0) and assumes single-line UTF-8 JSONL, so its results can differ from jq's on the same query. zog(file) uses two threads (reader plus scanner) against single-threaded jq. ripgrep cannot express numeric comparisons natively, so its rows are some unstated regex approximation. A tool-versus-tool result, not a language comparison; arguably belongs in a JSON category as much as text. [retier] First-party only: no CPU, benchmark script, dataset, baseline versions or flags, and jq and jaq share one column. zog does different and weaker work than jq: it does not parse or validate JSON, ignores nesting, matches numbers literally and assumes single-line UTF-8 JSONL. Correctness bugs in the measured code (src/scanner.zig, present at benchmarked commit 7e83065): the WHERE matcher accepts any occurrence of the quoted key text with no colon check (`error exists` matches {"level":"error"}) and neq is true if any occurrence differs; --format json leaves strings unquoted when the first byte is a digit, '-', 't', 'f' or 'n' and truncates objects and arrays, so the JSON re-formatting row is not equivalent to jq; single-field SELECT and aggregates can return an empty value (sum undercounts); unchecked i64 overflow on 19+ digit integers; lines over 8 MiB end the scan. README numbers date from 2026-02-27, before the Zig 0.16 std.Io port (v1.0.0 unmeasured); the Linux release is built for baseline x86-64 (SSE2, not AVX2).

Query language is limited to the supported match, extract and aggregate forms; it is a filter tool, not a general jq replacement.

## Maintenance

Small single-author MIT tool (27 commits, 49 stars, no issues filed). v1.0.0 (2026-07-17) is a contributor's port to Zig 0.16 std.Io. Nobody has re-measured since that port: the README numbers predate it and the March 2026 feature commit. `zog --version` still prints 0.1.5, and the README's Linux download URL (zog-linux-x64) does not match the released asset name zog-linux-amd64.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** First-party README table only: no benchmark script in the repository (src holds only main.zig and scanner.zig), no CPU model, no versions or build flags for zog, jq, jaq or ripgrep, and jq and jaq share one column. The largest ratio (about 58x) exceeds 50x with flags unstated, so C is also the cap.
- **Retiered** C to D: Enricher: the measured queries run a matcher that gives different answers from jq (key text matched anywhere without a colon check, neq true if any occurrence differs, single-field aggregates that drop values) and the JSON re-formatting row emits invalid JSON for many inputs, on top of first-party numbers with no script, dataset or CPU; no like-for-like measurement against jq remains: D.
- **Verifier notes:** Numbers match the README; the record omitted the zog(pipe) column and the field-extraction and re-formatting rows, now added. Shortcomings to record: first-party, no script, CPU or baseline versions; jq/jaq merged column; zog trades correctness (nesting-blind, literal numeric matching, no validation) for speed, so it is not doing the same job as jq; tool-versus-tool, not a Zig-versus-C win.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-38 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/aikoschurmann/zog>
  - <https://github.com/aikoschurmann/zog/commits>
  - <https://github.com/aikoschurmann/zog/tree/main/src>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/HEAD/README.md>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/HEAD/build.zig>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/HEAD/src/main.zig>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/HEAD/src/scanner.zig>
- **Sources the enricher read:**
  - <https://github.com/aikoschurmann/zog>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/HEAD/README.md>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/HEAD/build.zig>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/HEAD/src/main.zig>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/HEAD/src/scanner.zig>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/HEAD/.github/workflows/release.yml>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/7e83065/src/scanner.zig>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/e7e7ca3/README.md>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/548f657/README.md>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/7e83065/README.md>
  - <https://raw.githubusercontent.com/aikoschurmann/zog/1c02e64/README.md>
  - <https://github.com/aikoschurmann/zog/commits>
  - <https://github.com/aikoschurmann/zog/commits/main/README.md>
  - <https://github.com/aikoschurmann/zog/issues?q=is%3Aissue>
  - <https://github.com/aikoschurmann/zog/releases>
  - <https://github.com/aikoschurmann/zog/releases/expanded_assets/v1.0.0>
  - <https://github.com/aikoschurmann/zog/pull/2>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/aikoschurmann/zog`) · [data/wave14/enrich/raw/github_com_aikoschurmann_zog.json](../../../data/wave14/enrich/raw/github_com_aikoschurmann_zog.json) (enrichment confidence 0.6)

</details>
