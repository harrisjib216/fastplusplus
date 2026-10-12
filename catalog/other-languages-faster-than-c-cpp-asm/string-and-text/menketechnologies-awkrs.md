# awkrs (Rust AWK)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `Rust` · `MIT` · 🟢 active

> AWK implementation in Rust with a fused bytecode VM; its single-rule fast paths run 2-5x faster than mawk on 1M-line files.

| | |
|---|---|
| **Beats** | mawk 1.3.4 and GNU gawk 5.4.0 (C); BSD awk on macOS also timed |
| **Claimed result** | README tables (hyperfine mean ms on 1M-line inputs, Apple M5 Max). Rows are awkrs (JIT) / awkrs (bytecode) vs mawk 1.3.4 vs gawk 5.4.0. { print \$1 }: 15.7 / 16.1 vs 66.2 vs 100.8 (mawk relative 4.22x). Sum first column: 13.0 / 12.9 vs 37.5 vs 62.9 (2.90x). Multi-field print: 56.4 / 55.8 vs 156.6 vs 266.1 (2.81x). Regex filter: 11.1 / 11.1 vs 19.3 vs 351.4 (mawk 1.74x, gawk 31.72x). Associative array: 340.0 / 343.7 vs 610.0 vs 342.4 (parity with gawk). NR%2 field print: 30.2 / 30.7 vs 71.1 vs 116.1 (2.36x). Field computation: 19.0 / 18.8 vs 57.7 vs 100.5 (3.08x). String concat print: 51.0 / 50.5 vs 121.0 vs 182.2 (2.39x). No-match gsub: 13.8 / 13.9 vs 74.3 vs 436.3 (mawk 5.39x). CPU-bound BEGIN loop: 9.2 / 9.6 vs 9.7 vs 20.7 (mawk 1.06x, within noise). Generated 2026-04-10 with awkrs 0.1.18. The README says the bytecode row represents today's default path for these programs. |
| **Workload** | hyperfine on 1,000,000-line inputs: '{ print \$1 }', sum of first column, multi-field print, regex filter, associative-array count, conditional field print, field arithmetic, string concatenation, no-match gsub, plus a CPU-bound BEGIN loop. |
| **Metric** | latency |
| **Hardware** | Apple M5 Max, macOS arm64 |
| **Compiler and flags** | awkrs: cargo build --release with the default release profile (no [profile.release] in Cargo.toml, so opt-level 3, no LTO); rustc version not stated. Baselines: Homebrew bottles /opt/homebrew/bin/gawk (GNU Awk 5.4.0) and /opt/homebrew/bin/mawk (1.3.4 20260302), build flags not stated. BSD awk is /usr/bin/awk. Locale is not pinned (the script does not set LC_ALL). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Why it wins** | README: on regular files a raw byte path parses the Nth whitespace field straight from an mmap'd buffer, a 'slurp inline' path does a byte memmem scan for gsub, and a fused-superinstruction bytecode VM runs the rest; optional rayon parallelism (-j, default 1) and a fusevm/Cranelift numeric offload that does not engage on these string/field programs. |
| **Adoption** | 1 star, 0 forks, 604 commits; crates.io 2,037 downloads (awkrs 0.5.7) |
| **Last commit** | 2026-10-11 |
| **Links** | [repository](https://github.com/MenkeTechnologies/awkrs) · [benchmark](https://github.com/MenkeTechnologies/awkrs) |

## Verdict

One first-party hyperfine run (2026-04-10, awkrs 0.1.18, Apple M5 Max, macOS, 1M-line seq-generated files, mean of at least 10 runs after 3 warm-ups) shows the bytecode build at 16.1 ms vs mawk 1.3.4 66.2 ms and gawk 5.4.0 100.8 ms for { print \$1 } (4.1x mawk), 2.3-3.1x mawk on the summing and field-print programs, 5.3x mawk and 31x gawk on no-match gsub, and parity with gawk on associative-array counting and with mawk on a CPU-bound BEGIN loop (ratios derived from page data); outputs were not cross-checked and the benchmarked programs all take inline fast paths.

## Use it when

- Shell pipelines running one-rule awk one-liners (print fields, sum a column, count literal matches, no-match gsub) over large regular files, where the README measured 2.3-5.4x mawk 1.3.4 and 3.6-31x gawk 5.4.0 on an Apple M5 Max.
- Literal-substring filters or gsub on files where gawk is slow in a UTF-8 locale: /alpha/ counting took 11.1 ms vs gawk 351 ms and mawk 19.3 ms on 1M lines.
- Teams that want gawk extensions (CSV mode, arrays of arrays, PROCINFO["sorted_in"], -M bignums) in a single Rust binary, installable with cargo install or Homebrew.
- Embarrassingly parallel per-record programs on multi-core machines, via -j N with output reordered to input order (not part of the measured numbers).

## Skip it when

- Multi-rule or multi-statement programs: they leave the inline fast paths and run on the bytecode VM, whose only measured case (a CPU-bound BEGIN loop) ties mawk (9.6 vs 9.7 ms), and associative-array counting only ties gawk (343.7 vs 342.4 ms).
- Numeric columns with units, suffixes, hex under -n, or NaN/Inf strings: the { s += \$N } and { s += \$a \* \$b } fast paths parse fields differently from awk (see gotchas) and can return different sums.
- CRLF files where output bytes matter: the inline paths drop the trailing CR that the rest of awkrs, gawk and mawk keep.
- Huge single files piped into head or a slow consumer: the inline loops append to one output buffer for the whole file with no flush inside the loop, so memory grows with output size and nothing is written until the loop ends.
- Scripts needing gawk's interactive debugger, per-line profiler, arbitrary @load .so extensions or audited multibyte field splitting (documented gaps); the project has 1 star and no third-party users on record.

## How it is fast

Programs compile to a stack bytecode VM with peephole superinstructions (print \$N becomes PrintFieldStdout, s += \$N becomes AddFieldToSlot) and slot-indexed scalars. Regular files are memory-mapped, and a single-rule program whose body is one fused opcode skips the VM entirely: detect_inline_program in src/lib.rs routes { print \$N }, { s += \$N }, { s += \$a \* \$b }, { print \$a, \$b, \$c }, { print \$a "sep" \$b }, { a[\$N] += k }, /literal/ { c += k }, NR % m == k { print \$N } and { gsub("lit", "repl"); print } to hand-written byte loops that find fields by scanning raw bytes, match literals with memchr's memmem and append output to one buffer. Every one of the nine 1M-line benchmark programs hits one of these shapes; the only benchmark that runs through the VM (the BEGIN loop) ties mawk.

## Compared with alternatives

Pick awkrs over eBay TSV Utilities, hck or tuc when you need actual awk programs rather than fixed cut or filter verbs, and over the catalogued frawk when you want gawk extension coverage and POSIX awk syntax; prefer tsv-utils, hck or tuc for column selection and filtering at scale, since their claims do not rest on one-rule special cases.

## Integration

| | |
|---|---|
| **Form** | crate (command-line binaries awkrs and aw; cargo install awkrs or a Homebrew tap; also builds a lib and staticlib for its AOT mode) |
| **Dependencies** | Many crates, including fusevm, cranelift-\* 0.130, regex, memchr, memmap2, rayon, reedline, lsp-server and rug with gmp-mpfr-sys, which needs a C compiler and make at build time |
| **Minimum toolchain** | Rust 2021 edition; no rust-version (MSRV) declared in Cargo.toml or on crates.io |
| **Platforms** | Unix (benchmarked on macOS arm64; CI builds mawk on Ubuntu for parity runs); Windows not documented |
| **Thread safety** | Not applicable for the CLI; -j N runs parallel-safe programs on rayon workers with per-worker runtime state and does not merge record-rule mutations into END. |
| **Drop-in for the baseline** | partial — same command-line surface and most gawk extensions, but documented gawk gaps, and the inline fast paths differ from awk on CRLF input and on non-integer numeric fields |

## Gotchas

- Correctness bug in the benchmarked numeric fast paths: process_file_add_field_to_slot_raw and process_file_add_mul_fields_to_slot_raw (the paths behind the 'sum first column' and 'field computation' rows) parse each field with parse_number_bytes, which accepts only a whole-field integer or Rust's str::parse::&lt;f64&gt;, while the VM path uses awk's longest-numeric-prefix rule. A field such as '12ms' or '3.5%' adds 0 instead of 12 or 3.5, 'nan' or 'inf' turns the sum into NaN or Inf where gawk reads 0, and -n (hex/octal coercion) is ignored, so the same sum written as two statements gives a different answer. The fallback also calls from_utf8_unchecked on raw field bytes, which is undefined behaviour in Rust for non-UTF-8 input.
- CRLF divergence in the fast paths: all five inline loops strip a trailing CR before the newline, while awkrs's own record splitter (record_io.rs split_lines_unix) keeps it 'for gawk parity', so { gsub("lit", "x"); print } on a CRLF file emits LF-only lines, and with a non-default FS the last field loses its CR, unlike gawk, mawk and awkrs's VM path. The 2026-10-08 commit '-j: parallel workers keep a record's trailing CR and newline' fixed the same issue in parallel mode only.
- The README numbers are stale and benchmark-shaped: generated 2026-04-10 on awkrs 0.1.18 (the crate is now 0.5.7), the JIT rows come from a Cranelift module that has since been removed (README caveat of 2026-06-01), every input is seq-generated integers with LF line endings (which trigger neither bug above), outputs are never compared across engines, a compiler comment (normalize_field_indices in src/compiler.rs) records that the field-index fusions these paths depend on once stopped firing on real programs after a parser change, and the locale is not pinned, so gawk's 351 ms regex and 436 ms gsub rows may reflect multibyte matching.
- Baselines are Homebrew gawk 5.4.0 and mawk 1.3.4 with unknown build flags; each 10-60 ms hyperfine mean includes process startup, and awkrs maps the file with mmap while gawk and mawk read it through read().

## Known shortcomings

- Measured on 0.1.18 (now 0.5.7); wins come from mmap and raw-byte special paths, not Rust codegen; Homebrew gawk and mawk flags unknown and the locale unpinned, so the gawk regex and gsub rows (13.8 vs mawk 74.3 vs gawk 436.3) are suspect; 1 star.
- All nine file benchmarks hit single-rule inline fast paths; only the BEGIN loop uses the VM, where it ties mawk. Correctness bugs in the benchmarked paths: the sum and field-computation raw paths use parse_number_bytes (a whole-field parse with no awk numeric prefix, so '12ms' counts as 0, bare nan/inf poison sums, -n is ignored, from_utf8_unchecked is UB); five inline loops strip CR while the VM path keeps it. The bench inputs (sequential integers, LF) hide both. The JIT rows came from a Cranelift module since removed.

## Caveats and trade-offs

First-party, single machine (Apple M5 Max, macOS 25.4). Numbers are from awkrs 0.1.18 (2026-04-10) while the crate is now 0.5.7, so they have not been re-run on current code. The README's 2026-06-01 caveat says the JIT rows came from a Cranelift module that has since been removed; the bytecode rows are within 0.5 ms. The wins come from special-cased fast paths, not from Rust codegen: single-rule programs such as { print \$1 }, { s += \$1 } and no-match literal gsub are recognised and run as raw byte scans over an mmap'd file, skipping the VM. The baselines run their general record loops through read(). Baseline flags are unknown (Homebrew bottles, probably distro-default -O2, not a verified -O3). The locale is not set, and gawk's 351 ms regex and 436 ms gsub rows may reflect UTF-8 multibyte matching, while awkrs works on bytes. Each hyperfine time includes process startup on 10-25 ms runs. Parity only on the associative-array case (gawk) and the BEGIN loop (mawk). The repo has 1 star and no third-party reproduction. [retier] All nine file benchmarks hit single-rule inline fast paths; only the BEGIN loop uses the VM, where it ties mawk. The benchmarked raw paths use parse_number_bytes (a whole-field parse with no awk numeric prefix, so '12ms' counts as 0, bare nan/inf poison sums, -n is ignored, from_utf8_unchecked is UB) and five inline loops strip CR while the VM path keeps it; the bench inputs (sequential integers, LF) hide both. The JIT rows came from a Cranelift module since removed.

Not a full gawk (documented parity gaps: interactive debugger, extension loading, multibyte field splitting not audited); parallel mode only for parallel-safe programs.

## Maintenance

Very active (604 commits, last commit 2026-10-11, crate 0.5.7 with 2,037 downloads, MIT) and pursuing gawk parity with a large parity corpus, but it has 1 star, no issue tracker activity, benchmark numbers six months and five minor versions old, and fast paths that still diverge from awk semantics on CRLF and non-integer numeric fields.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now D.
- **Tier reason:** The README tables are copied verbatim from benchmarks/benchmark-results.md, which scripts/benchmark-vs-awk.sh generates. Code and CPU (Apple M5 Max) are public. The rustc version is not stated, and gawk/mawk are Homebrew bottles (/opt/homebrew/bin) with unknown build flags. First-party, missing compiler and baseline flags, so tier C.
- **Retiered** C to D: Enricher: every file benchmark runs a single-rule inline fast path whose numeric parsing and CR handling diverge from awk (the bench inputs hide it), the JIT rows came from a since-removed module, and the numbers were never re-run on current code; measured paths compute a different function from the baseline (stb-zip-style divergence, kept and documented): C to D.
- **Verifier notes:** Numbers match the README and benchmarks/benchmark-results.md exactly; the record omitted the gsub row (now added). Keep at C with these shortcomings: stale (measured on 0.1.18), wins from mmap/raw-byte special-case paths rather than the language, Homebrew baseline flags unknown, locale unpinned (gawk regex/gsub rows suspect), 1 star. Metadata checked: MIT, last commit 2026-10-11, not a fork, not archived.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-81 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/MenkeTechnologies/awkrs>
  - <https://github.com/MenkeTechnologies/awkrs/commits>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/README.md>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/scripts/benchmark-vs-awk.sh>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/benchmarks/benchmark-results.md>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/Cargo.toml>
  - <https://crates.io/api/v1/crates/awkrs>
- **Sources the enricher read:**
  - <https://github.com/MenkeTechnologies/awkrs>
  - <https://github.com/MenkeTechnologies/awkrs/commits/main>
  - <https://github.com/MenkeTechnologies/awkrs/issues?q=is%3Aissue>
  - <https://github.com/MenkeTechnologies/awkrs/tree/main/src>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/README.md>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/scripts/benchmark-vs-awk.sh>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/benchmarks/benchmark-results.md>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/BUGS.md>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/src/record_io.rs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/src/runtime.rs>
  - <https://crates.io/api/v1/crates/awkrs>
  - <https://raw.githubusercontent.com/MenkeTechnologies/awkrs/HEAD/src/compiler.rs>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/menketechnologies/awkrs`) · [data/wave14/enrich/raw/github_com_menketechnologies_awkrs.json](../../../data/wave14/enrich/raw/github_com_menketechnologies_awkrs.json) (enrichment confidence 0.6)

</details>
