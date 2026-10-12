# hexdump-rs (Rust hexdump -C replacement)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Systems and safety](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `Apache-2.0` · 🔴 abandoned

> Single-file Rust re-implementation of hexdump -C only; about 40x faster than the system hexdump on non-repeating input.

| | |
|---|---|
| **Beats** | system hexdump -C (C; implementation and version not stated, likely util-linux or BSD hexdump) |
| **Claimed result** | Hyperfine screenshots in the README (img/\*.png): dev-random 708.6 ms vs 16.9 ms (42.00x faster); test.mca 617.1 ms vs 16.0 ms (38.62x); no-squeeze.bin 646.3 ms vs 17.1 ms (37.86x); zeros.bin 658.2 ms vs 338.5 ms (1.94x). README text says 'up to a 14x speedup' while the repository description says 'up to 40x faster'. |
| **Workload** | Canonical hex+ASCII dump (hexdump -C) of four files with hyperfine -m 100 --warmup 5: 10 MB from /dev/random, a 7.8 MB semi-random file (test.mca), an 8.5 MB file whose lines all differ (no squeezing) and a 1.1 GB file of zeros. |
| **Metric** | latency |
| **Compiler and flags** | cargo release build (./target/release/hexdump-rs); Cargo.toml release profile only adds debug = true for flamegraphs; no C build flags (system hexdump binary as installed). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Adoption** | 0 stars, 1 fork (3 commits) |
| **Last commit** | 2023-08-15 |
| **Links** | [repository](https://github.com/funnyboy-roks/hexdump-rs) · [benchmark](https://github.com/funnyboy-roks/hexdump-rs) |

## Verdict

Hyperfine screenshots (-m 100, 5 warm-ups, output discarded, machine, OS and hexdump implementation not stated) show the system hexdump -C against a release build of commit 085158f: 708.6 vs 16.9 ms on 10 MB from /dev/random (42.00x), 617.1 vs 16.0 ms on a 7.8 MB semi-random .mca file (38.62x), 646.3 vs 17.1 ms on the 8.5 MiB no-squeeze.bin from test-files/filegen.py (37.86x) and 658.2 vs 338.5 ms on 1 GiB of zeros where both tools squeeze (1.94x). The gap comes from replacing a printf-per-conversion format interpreter with hard-coded formatting, not from the language.

## Use it when

- Dumping large regular files with hexdump -C layout when the system hexdump is too slow, for example tens of MB to GB of binary data piped to less or grep.
- As a reference for how much a specialised formatter gains over a format-string interpreter (about 40x on random data, under 2x when nearly everything is squeezed).
- Files under 4 GiB whose length is a multiple of 16 or whose tail you do not care about, where '!' and '\~' showing as '.' is acceptable.

## Skip it when

- Anywhere byte-exact hexdump -C output matters (diffs, golden files, scripts): the ASCII column, squeeze markers, offsets past 4 GiB and short final lines all differ from util-linux hexdump.
- When you need -n/--length: it is silently ignored, so the whole input is dumped.
- Streaming stdin from a pipe whose writes are not 16-byte aligned: each line is filled by a single read() call, so a short read prints a short line and shifts every later offset (inference from print_canonical; not tested in the repo).
- Any other hexdump mode (-b, -c, -d, -o, -x, -e format strings): not implemented.
- Production use: 3 commits, 0 stars, no releases or crates.io package, last commit 2023-08-15, and errors exit with status 0.

## How it is fast

It hard-codes the one -C layout: each 16-byte block is formatted into a reused 79-byte Vec with a 16-entry hex nibble lookup table, an unrolled 8-nibble offset writer and a range check for printable bytes, then written through a BufWriter. util-linux hexdump (the likely baseline; the README does not name it) instead walks a parsed format-unit list and calls printf once per conversion (one per hex byte, one per ASCII byte via %_p, one for the address), which is what dominates its 600-700 ms on 8-10 MB inputs. The commit that moved from the README's 14x to about 40x ('Mostly remove branching') removed per-byte branches and unwrap calls from render_bytes and render_ascii.

## Compared with alternatives

No other hex dumper is catalogued in this category; unlike packaged siblings such as fd or neosmart's tac, hexdump-rs is a three-commit hobby project, so treat it as a small, Apache-2.0 code sample for a fast canonical dump loop rather than a tool to install.

## Integration

| | |
|---|---|
| **Form** | crate (binary only, build from source with cargo; not published) |
| **Dependencies** | clap 4.3 (derive) |
| **Minimum toolchain** | Rust 2021 edition; minimum rustc not documented |
| **Platforms** | any std target; no platform-specific code |
| **Thread safety** | single-threaded CLI; not applicable |
| **Drop-in for the baseline** | partial — same invocation and layout as hexdump -C for regular files under 4 GiB, but '!' and '\~' print as '.', a single repeated line is dropped without the '\*' marker, a final line of 9-15 bytes shows stale bytes in the hex column, offsets wrap at 4 GiB, and -n is ignored |

## Gotchas

- Output bugs introduced by the same commit (085158f, 2023-08-15) that produced the \~40x screenshots, all absent from the initial commit: render_ascii's range b'"'..=b'}' prints '!' (0x21) and '\~' (0x7e) as '.'; the second render_bytes call passes read_count instead of read_count - 8, so a final partial line of 9-15 bytes prints the previous line's sanitised bytes (for example '2e 2e 2e 2e') where hexdump pads with spaces; the new three-state squeeze drops a single repeated line without printing '\*'; and end = (i + length).max(usize::MAX) ignores -n. A Python transcription of print_canonical reproduces each case. None of these adds a fast path for the benchmarked files (full 16-byte lines are formatted the same way), so the timings stand, but no output check was run: hyperfine discards both tools' output and the tests compare only two tiny inputs.
- The offset writer emits only the low 32 bits (8 nibbles), so offsets wrap to 00000000 at 4 GiB; util-linux hexdump prints the address as a long long with %08.8 (a minimum width) and keeps counting. The hex_fn test only covers values below u32::MAX.
- -s/--skip allocates a zeroed Vec of the skip size and does one read() into it instead of seeking, so a large skip costs that much memory and a short read skips less than asked.
- main() prints errors (missing file, broken pipe) to stderr but always exits with status 0. The README's hyperfine command names ./target/release/hexdump while the screenshots ran ./target/release/hexdump-rs, and the README text still says 14x while the description and screenshots say about 40x.

## Known shortcomings

- Specialised layout against the generic hexdump format interpreter; no CPU or hexdump version; the README says 14x while the repo description says 40x; output differs from hexdump -C ('!' and '\~' printed as '.', a single repeated line dropped without '\*', -n ignored).
- Output regressions introduced by the same commit (085158f) that produced the about 40x screenshots, absent from the initial commit: '!' and '\~' print as '.'; a final 9-15-byte line shows stale bytes in the hex column (the second render_bytes gets read_count, not read_count-8); a single repeated line is dropped without '\*'; -n is ignored ((i+length).max(usize::MAX)); offsets wrap at 4 GiB; -s allocates a skip-sized Vec; exit status always 0. None is a fast path for the benchmarked files, so the timings stand, but hyperfine discards output and nothing checks it. The gap comes from util-linux's printf-per-conversion format interpreter against a hard-coded layout.

## Caveats and trade-offs

Different algorithm: system hexdump drives a generic format-string interpreter while src/main.rs hard-codes the one canonical layout with a hex lookup table and a BufWriter, so the 40x gap is a specialisation effect, not a language effect (inference; the README gives no mechanism). CPU, OS, hexdump implementation and version are not stated; hyperfine discards both tools' output; the numbers exist only as screenshots (which match the claimed figures), and the README text (14x, apparently from before the 2023-08-15 commit 'now \~40x speed difference') disagrees with the screenshots (up to 42x). The zeros.bin row (1.94x) is where both tools squeeze repeated lines. Output is not identical to hexdump -C: render_ascii prints '!' (0x21) and '\~' (0x7e) as '.', a run of exactly one repeated line is dropped without the '\*' marker, and -n/--length is ignored because end = (i + length).max(usize::MAX); the tests check helpers and two tiny inputs, never output against the real hexdump. These differences do not create a fast path (every line is still formatted), so the numbers stand. Tiny hobby repo (0 stars, 1 fork, 3 commits), last commit 2023-08-15. [retier] Output regressions introduced by the same commit (085158f) as the about 40x screenshots: '!' and '\~' print as '.'; a final 9-15-byte line shows stale bytes in the hex column; a single repeated line is dropped without '\*'; -n is ignored; offsets wrap at 4 GiB; -s allocates a skip-sized Vec; exit status always 0. hyperfine discards output and nothing checks it. The gap comes from util-linux's printf-per-conversion format interpreter against a hard-coded layout.

Implements only hexdump -C, not hexdump's format-string language, and is 'meant as a drop-in replacement for hexdump -C' only.

## Maintenance

Abandoned hobby repo (last commit 2023-08-15, 0 stars, no release) under Apache-2.0 and small enough to read in one sitting, but its fastest version has unfixed output bugs ('!' and '\~' masked, stale bytes on short final lines, missing '\*' for single repeats, -n ignored, 32-bit offsets), so it is not a safe drop-in for hexdump -C.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party hyperfine screenshots (img/dev-random.png, test.mca.png, no-squeeze.bin.png, zeros.bin.png) show exactly the claimed means and ratios against system hexdump -C, with the hyperfine command in the README, but no CPU, OS, hexdump implementation/version or C build flags; the test files are generated locally and not published.
- **Verifier notes:** Screenshots confirm 42.00x, 38.62x, 37.86x and 1.94x; tier C stands. Shortcomings to record: specialised tool vs generic format interpreter (not a language effect), no hardware/hexdump version, README text says 14x vs 40x in description, output deviates from hexdump -C ('!' and '\~' shown as '.', single repeated line dropped without '\*', -n ignored), abandoned 0-star repo.
- **Fields the verifier corrected:** `caveats`, `stars_or_usage`
- **Shortcomings recorded by:** verifier batch-87 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/funnyboy-roks/hexdump-rs>
  - <https://github.com/funnyboy-roks/hexdump-rs/commits>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/img/dev-random.png>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/img/test.mca.png>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/img/zeros.bin.png>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/img/no-squeeze.bin.png>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/src/test.rs>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/src/cli.rs>
- **Sources the enricher read:**
  - <https://github.com/funnyboy-roks/hexdump-rs>
  - <https://github.com/funnyboy-roks/hexdump-rs/commits>
  - <https://github.com/funnyboy-roks/hexdump-rs/commit/085158fa840388049d35d1a7d2aaa1feb8d76a99>
  - <https://github.com/funnyboy-roks/hexdump-rs/tree/main/test-files>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/Cargo.lock>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/src/cli.rs>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/src/test.rs>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/test-files/filegen.py>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/test-files/.gitignore>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/b7aad38ad7290e0ad6f0c2947effd1c381c3bdac/src/main.rs>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/img/dev-random.png>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/img/test.mca.png>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/img/no-squeeze.bin.png>
  - <https://raw.githubusercontent.com/funnyboy-roks/hexdump-rs/HEAD/img/zeros.bin.png>
  - <https://raw.githubusercontent.com/util-linux/util-linux/master/text-utils/hexdump.c>
  - <https://raw.githubusercontent.com/util-linux/util-linux/master/text-utils/hexdump-display.c>
  - <https://raw.githubusercontent.com/util-linux/util-linux/master/text-utils/hexdump-parse.c>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/funnyboy-roks/hexdump-rs`) · [data/wave14/enrich/raw/github_com_funnyboy_roks_hexdump_rs.json](../../../data/wave14/enrich/raw/github_com_funnyboy_roks_hexdump_rs.json) (enrichment confidence 0.8)

</details>
