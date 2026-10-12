# fastgron

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [JSON](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C++` · `MIT` · 🟢 active

> C++20 simdjson-based CLI that flattens JSON into greppable gron assignments and back; \~50-80x faster than gron.

| | |
|---|---|
| **Beats** | gron |
| **Claimed result** | 50x faster than gron on big files (400MB/s input / 1.8GB/s output on M1 MacBook Pro). Speed section on citylots.json (\~190MB): fastgron 0.447s vs gron --no-sort 36.705s (\~82x, derived from page data); fastgron --sort 1.464s vs gron 1:25.80 (\~59x, derived from page data). Ungron of the 840MB gron file: fastgron 6.122s, while gron -u was killed. Path lookup: fastgron 0.176s vs jq 3.252s ('18x') and jj 0.972s ('5x'). |
| **Workload** | Converting large JSON files into greppable gron-style key=value assignments (JSON to GRON) and back (ungron), benchmarked on the public \~190MB citylots.json (sf-city-lots-json) with shell `time` |
| **Metric** | throughput |
| **Hardware** | Apple M1 MacBook Pro |
| **Adoption** | 678 stars |
| **Last commit** | 2026-07-04 |
| **Links** | [repository](https://github.com/adamritter/fastgron) · [benchmark](https://github.com/adamritter/fastgron#readme) |

## Verdict

Single shell `time` runs on an M1 MacBook Pro (hardware named only in the headline; compiler not stated, CMakeLists forces -O3 -g) on the public \~190MB citylots.json: fastgron 0.447s vs Go gron --no-sort 36.705s (\~82x) and fastgron --sort 1.464s vs default gron 1:25.80 (\~59x), with gron using 117-189% CPU. Ungron of the 840MB gron file took 6.122s in the timing block (the README prose says 8s) while gron -u was killed after 1:07.75, and a single-path lookup took 0.176s vs jq 3.252s and jj 0.972s.

## Use it when

- Grepping or exploring JSON files from hundreds of MB to a few GB that fit in RAM, where gron takes tens of seconds to minutes (README: 190MB citylots.json in 0.45s vs 36.7s for gron --no-sort).
- Shell pipelines like `fastgron big.json | rg pattern | fastgron -u` to cut a subset of a large document back out as JSON; the README ungrons an 840MB gron file in \~6s where gron -u was killed.
- One-off path lookups in a big file from the shell with gron-style path output instead of jq syntax (0.176s vs jq 3.252s and jj 0.972s on citylots).
- Replacing gron in interactive use or scripts that already pass `--no-sort` or do not depend on key order, on Linux, macOS (x86_64 and Apple Silicon) or Windows.

## Skip it when

- Inputs that do not fit comfortably in RAM: the whole file is loaded into a SIMD-padded buffer (no mmap; the author says simdjson's padding requirement blocks it), and a user measured \~1.5x the input size resident (issue #22); stdin input is read into a std::string and then copied again into a padded_string.
- Ungronning very large gron files: ungron builds a full std::map/std::vector/std::variant tree, and a user measured 19GB peak on macOS and 39GB on Linux ungronning a \~9GB gron file (issue #19, v0.7.6 era).
- Scripts that depend on gron's exact CLI or output: default output is unsorted (gron sorts by default), `-v` means invert-match rather than gron's `--values`, and gron's `--json`, `--values`, `-m` and `-k` are missing; gron's documented exit codes are not replicated.
- Untrusted or possibly malformed input: parse errors surface as an uncaught `simdjson::simdjson_error` that aborts the process (issue #15 shows `terminate called after throwing ... SCALAR_DOCUMENT_AS_VALUE` on non-JSON input; main() has no try/catch), and GRON.md lists top-level scalar documents as unsupported (future work).
- When you need an embeddable library or an actively developed tool: there is no library API (listed only as a future idea), and the last functional release is v0.7.7 (Dec 2023).

## How it is fast

Parsing uses simdjson's On-Demand API (vendored simdjson 3.1.8 with runtime CPU-kernel dispatch): SIMD stage-1 structural indexing, no DOM, and scalars are copied to the output as their raw JSON token text (`raw_json_token()`) with no number or string decode/re-encode. Each line is assembled with memcpy into a reusable path buffer (`growing_string`, which never shrinks) and a 1MB batched output buffer flushed with raw `write(2)`, avoiding per-line allocation and iostreams. The default output is unsorted document order; `--sort` buffers each object's children and `std::sort`s them by key, costing \~3x (1.464s vs 0.447s on citylots). Path queries (`-p`) iterate with On-Demand and print only the matching branches.

## Compared with alternatives

Pick fastgron over simdjson when you want a ready-made shell tool rather than a library to embed (fastgron is simdjson plus a gron printer and has no API of its own), and over jist when you need the whole document flattened for grep or an ungron round trip rather than extracting one path from a multi-GB file. For in-process C++ JSON work, use simdjson or yyjson directly.

## Integration

| | |
|---|---|
| **Form** | source-drop (standalone CLI executable built with CMake; prebuilt Linux/macOS/Windows binaries on the v0.7.7 release, Homebrew `--build-from-source`, AUR `fastgron-git`, Nix flake); no library API |
| **Dependencies** | simdjson 3.1.8 (vendored amalgamation in extern/simdjson); optional libcurl for http/https input (the Windows release binary is built without it) |
| **Minimum toolchain** | C++20 compiler and CMake 3.14+ (README says CMake 3.8+, but CMakeLists.txt sets cmake_minimum_required 3.14 and forces Release with -O3 -g plus \$CXX_ARCH_FLAGS); release CI uses the default compiler on ubuntu-latest, MinGW on Windows and Homebrew LLVM 15 clang on macOS |
| **Platforms** | Linux, macOS (universal x86_64 + arm64 build), Windows (MinGW); simdjson selects the SIMD kernel at runtime (`--simdjson-version` prints the detected one). The Windows fastgron.exe release is compiled with -march=icelake-client, with a separate -without-simd binary; the Ubuntu release binary needs glibc 2.34+ (issue #12, open). |
| **Thread safety** | N/A: single-threaded CLI using global mutable state (output buffer, flags); the README lists a multithreaded NDJSON mode as a future idea |
| **Drop-in for the baseline** | partial — same gron line format and `-u/--ungron`, `-s`, `-c`, `--no-sort` flags, and gron can read its output (issue #17 pipes `fastgron --semicolon` into `gron -u`), but default output is unsorted (add `--sort` to match gron), `-v` means invert-match not `--values`, gron's `--json`, `--values`, `-m`, `-k` are absent, and error handling/exit codes differ |

## Gotchas

- `-s` stream mode calls simdjson `iterate_many` with the default 1,000,000-byte batch size, and simdjson 3.1.8 documents that the batch must be larger than the largest document, so NDJSON records over \~1MB should fail (from source reading, not tested).
- `--ungron -s` is meant to emit one JSON document per line, but print_json.cpp always separates object members with ",\n" even when newlines are turned off, so multi-key objects will span several lines (from source reading, not tested).
- Keys and values are written as raw JSON source text, so escape sequences and number spellings (e.g. big integers, 1.0e10) pass through unchanged, and `--sort` orders by raw escaped key bytes. Color is on automatically when stdout is a TTY and switches to match highlighting when `-F` is used.
- Ungron always emits object keys in sorted order (std::map), fills missing array indices with null, and had round-trip bugs fixed as late as v0.7.5-0.7.6 (issues #17, #19: dropped integer keys, doubled quotes, lost keys when one key was a prefix of another); parse_gron.cpp still carries a `TODO: implement escaping` comment.

## Known shortcomings

- No benchmark script, compiler or flags; single-machine README timings (M1 MacBook Pro) against gron, which is a slow Go baseline.
- Feature-frozen since v0.7.7 (2023-12); later commits are formatting/CI only. The gron -u baseline never finished, so ungron has no completed comparison. Loads the whole file (about 1.5x input RAM, #22); ungron of a \~9 GB file peaked at 19-39 GB (#19). Not a drop-in for gron: unsorted by default, -v means invert-match, --json/--values/-m/-k missing, bad input aborts with an uncaught simdjson error (#15). Vendored simdjson 3.1.8; no library API.

## Caveats and trade-offs

Compiler and build flags not stated (README asks only for a C++20 compiler plus CMake). The numbers are single shell `time` runs with no benchmark script, though the dataset (citylots.json) is public. The M1 MacBook Pro hardware is named in the headline sentence, not beside the timing runs. The baseline gron is a Go tool that used multiple cores (158% CPU) in the runs shown. The '50x' headline is conservative next to the \~59-82x implied by the page's own timings. fastgron's speed comes largely from simdjson.

Built on simdjson internally (does not itself beat simdjson); gron is a Go, single-threaded tool, so this is a JSON-processing-tool comparison rather than a raw parser/library comparison

## Maintenance

MIT-licensed, 678 stars and not archived, but the last functional release is v0.7.7 (2023-12-06) and the 2024-2026 commits (latest 2026-07-04) are formatting, Nix-flake and CI changes, so treat it as feature-frozen yet usable via prebuilt binaries, Homebrew, AUR or Nix.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The README states '50x faster than gron on big files (400MB/s input / 1.8GB/s output on M1 Macbook Pro)' and has a Speed section with shell `time` runs of fastgron and gron on the public citylots.json. There is no benchmark script, and compiler and flags are not stated (only 'C++20 compatible compiler' and a CMake build), so this is first-party evidence with partial methodology: tier C.
- **Verifier notes:** The record is accurate: the headline claim appears verbatim in the README and the Speed section backs it with timings against gron (plus jq and jj for path lookup). Metadata checked with gh: MIT, 678 stars, not a fork or archived, last commit 2026-07-04 (active).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/adamritter/fastgron#readme>
  - <https://github.com/adamritter/fastgron>
  - <https://api.github.com/repos/adamritter/fastgron>
  - <https://api.github.com/repos/adamritter/fastgron/commits?per_page=1>
  - <https://api.github.com/repos/adamritter/fastgron/readme>
- **Sources the enricher read:**
  - <https://github.com/adamritter/fastgron>
  - <https://github.com/adamritter/fastgron#readme>
  - <https://api.github.com/repos/adamritter/fastgron>
  - <https://api.github.com/repos/adamritter/fastgron/git/trees/HEAD?recursive=1>
  - <https://github.com/adamritter/fastgron/blob/main/CMakeLists.txt>
  - <https://github.com/adamritter/fastgron/blob/main/src/fastgron.cpp>
  - <https://github.com/adamritter/fastgron/blob/main/src/print_gron.cpp>
  - <https://github.com/adamritter/fastgron/blob/main/src/batched_print.hpp>
  - <https://github.com/adamritter/fastgron/blob/main/src/growing_string.hpp>
  - <https://github.com/adamritter/fastgron/blob/main/src/builder.hpp>
  - <https://github.com/adamritter/fastgron/blob/main/src/parse_gron.cpp>
  - <https://github.com/adamritter/fastgron/blob/main/src/jsonutils.hpp>
  - <https://github.com/adamritter/fastgron/blob/main/src/print_json.cpp>
  - <https://github.com/adamritter/fastgron/blob/main/src/print_filtered_path.cpp>
  - <https://github.com/adamritter/fastgron/blob/main/GRON.md>
  - <https://github.com/adamritter/fastgron/blob/main/scalar.json>
  - <https://github.com/adamritter/fastgron/blob/main/extern/simdjson/simdjson.h>
  - <https://github.com/adamritter/fastgron/blob/main/.github/workflows/ci.yml>
  - <https://github.com/adamritter/fastgron/blob/main/.github/workflows/build.yml>
  - <https://github.com/adamritter/fastgron/blob/main/.github/workflows/build-and-release.yml>
  - <https://github.com/adamritter/fastgron/issues?q=is%3Aissue>
  - <https://github.com/adamritter/fastgron/issues/12>
  - <https://github.com/adamritter/fastgron/issues/15>
  - <https://github.com/adamritter/fastgron/issues/16>
  - <https://github.com/adamritter/fastgron/issues/17>
  - <https://github.com/adamritter/fastgron/issues/19>
  - <https://github.com/adamritter/fastgron/issues/20>
  - <https://github.com/adamritter/fastgron/issues/22>
  - <https://github.com/adamritter/fastgron/pulls?q=is%3Apr>
  - <https://github.com/adamritter/fastgron/releases>
  - <https://api.github.com/repos/adamritter/fastgron/commits?per_page=15>
  - <https://github.com/tomnomnom/gron#readme>
  - <https://api.github.com/repos/tomnomnom/gron>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/adamritter/fastgron`) · [data/wave4/enrich/raw/github_com_adamritter_fastgron.json](../../../data/wave4/enrich/raw/github_com_adamritter_fastgron.json) (enrichment confidence 0.8)

</details>
