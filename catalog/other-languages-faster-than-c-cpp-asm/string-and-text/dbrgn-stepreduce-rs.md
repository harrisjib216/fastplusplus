# stepreduce-rs (Rust port of stepreduce)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `GPL-3.0-or-later` · 🟢 active

> Rust port of Seth Hillbrand's C++ stepreduce STEP CAD deduplicator; 5.2x faster than the std::regex C++ version, which has since caught up.

| | |
|---|---|
| **Beats** | stepreduce C++ original (uses libstdc++ std::regex) by Seth Hillbrand |
| **Claimed result** | README hyperfine: cpp-baseline 505.4 ms, rs-baseline 145.2 ms (about 3.5x), rs-find-numbers 104.5 ms, rs-prealloc 97.2 ms, which hyperfine reports as 5.20 +/- 0.10 times faster than the C++ original. A README note dated 2026-02-25 says that after optimizations (C++ issue #3) the C++ project is now slightly faster again than the Rust code. |
| **Workload** | Lossless size reduction of one 1 MiB STEP CAD text file (00010546_919044145dd24288a1945b5c_step_008.step), output to /dev/null, hyperfine with 3 warmups. |
| **Metric** | throughput |
| **Hardware** | AMD Ryzen 9 5900X |
| **Compiler and flags** | Not stated in the README and the bench/ directory is not committed. The Rust author's GitLab issue #3 (2026-02-14) asks whether 'cmake -DCMAKE_BUILD_TYPE=Release . && make' is the proper optimized build, implying a Release build of the C++ side; the C++ CMakeLists.txt sets no default build type (C++20, OpenCASCADE linked), so a plain cmake build would carry no -O flag. Rust side: Cargo release defaults (no custom [profile.release]; dev/test dependency opt-level 2). |
| **Kind** | library or program |
| **Same algorithm as the baseline** | yes |
| **Same optimization level** | not stated |
| **Why it wins** | README: 'probably attributable primarily to the use of the Rust regex crate' against the slow C++ std::regex, then about 1.5x more from finding numbers without a regex and preallocating. The attribution is the author's guess, not a profile. |
| **Adoption** | 0 stars |
| **Last commit** | 2026-03-01 |
| **Links** | [repository](https://github.com/dbrgn/stepreduce-rs) · [benchmark](https://github.com/dbrgn/stepreduce-rs) |

## Verdict

One hyperfine run (3 warmups) on a 1 MiB STEP file on an AMD Ryzen 9 5900X: the C++ stepreduce 2026-02-05 rewrite, which matched numbers, names and #refs with libstdc++ std::regex, took 505.4 ms, the first Rust port 145.2 ms, and the Rust build with a hand-written float scanner and preallocated maps 97.2 ms (5.20 +/- 0.10x); compiler versions and flags are not stated for either side. After C++ replaced its regexes on 2026-02-15, the Rust author reports the C++ about 4% faster (no published numbers), so the speed claim is obsolete.

## Use it when

- Embedding STEP size reduction in a Rust application (the LibrePCB use case) without the C++ toolchain; the C++ CMake build has required OpenCASCADE since 2026-02-15 (for its --check verification).
- Batch-minifying machine-generated STEP models (for example, component libraries) that repeat identical geometry entities, where file size matters more than keeping entity names.
- When you want the CDSR and SHAPE_REPRESENTATION_RELATIONSHIP root fixes, which keep assembly placements; C++ master has the first but not the second.
- Projects that can accept GPL-3.0-or-later code.

## Skip it when

- Speed alone: the README's own 2026-02-25 update says the C++ project is slightly faster again, and the author put it at about 4% on his test file (LibrePCB issue #1693).
- Files with non-UTF-8 bytes (for example, Latin-1 names written raw by some exporters): parsing stops silently at the first invalid line.
- Workflows that must keep every entity name or exact metadata: names are left out of the dedup key, and the -p and --use-step-precision options merge entities whose numbers differ beyond N decimals.
- Untrusted input on shared services: a '#' followed by more digits than fit in u32 panics, and a huge exponent such as 1E2000000000 makes normalize_number allocate gigabytes of '0' characters.
- Critical CAD pipelines without your own validation: it is an LLM-assisted port with 0 stars and no crates.io release, and the author disclaims correctness beyond the test suite.

## How it is fast

Same passes as the C++ original: repeated deduplication until a fixpoint, keyed on the entity text with numbers normalised and names blanked, followed by a reachability walk from root entity types. The 3.5x first step came from swapping libstdc++ std::regex for the Rust regex crate (lazy DFA) on the number, name and #ref patterns. A further 1.5x came from a hand-written float-literal scanner in place of the NUM_PATTERN regex, plus preallocating the dedup HashMaps. The repo has no profile, so the attribution is the author's.

## Compared with alternatives

No catalogued sibling handles STEP files; the real alternative is the C++ original (GitLab sethhillbrand/stepreduce), now about 4% faster per the Rust author, with built-in --check geometric verification through OpenCASCADE. Pick the Rust port for Rust embedding, a build without OpenCASCADE and the extra SHAPE_REPRESENTATION_RELATIONSHIP root fix, not for speed.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | regex; clap and anyhow for the optional CLI |
| **Minimum toolchain** | Rust edition 2024 with let-chains in lib.rs and normalize.rs, so Rust 1.88 or later in practice (no rust-version declared) |
| **Platforms** | any Rust target (pure Rust, no unsafe or platform code in src/) |
| **Thread safety** | not documented; reduce() is a pure function whose only statics are LazyLock&lt;Regex&gt;, so concurrent calls on separate inputs share no mutable state |
| **Drop-in for the baseline** | partial — the CLI takes the same input/output arguments, but output now differs from C++ master: Rust adds SHAPE_REPRESENTATION_RELATIONSHIP as a GC root and types complex '( ... )' entities by their first member, where C++ returns an empty type |

## Gotchas

- Silent truncation: parse.rs iterates BufRead::lines() and breaks on the first Err. A single non-UTF-8 byte (checked with a std-only test: a Latin-1 'ü' stopped a 9-line file after line 4) drops the rest of DATA and the whole footer, with no error returned. The CLI allows output to be the input path, so it can overwrite the original with a broken file.
- Orphan removal is a heuristic list of root types, and it has already lost geometry in real files twice: assembly placements were dropped until CDSR became a root (2026-02-15), and a proprietary model vanished in FreeCAD until SHAPE_REPRESENTATION_RELATIONSHIP was added (2026-03-01). The C++ original had the same bugs, and the benchmarked 2026-02-14 Rust builds predate both fixes. The author has proposed switching to an allow-list of collectable types.
- remap_references calls parse::&lt;u32&gt;().unwrap() on every '#\d+' match, including text inside quoted strings. A string such as '#12345678901' (u32 overflow) panics, as can non-ASCII digits, since the regex \d is Unicode-aware. The same pass rewrites '#N' inside string literals, a behaviour inherited from the C++ REF_PATTERN.
- Harness: bench/ binaries and build commands are not committed, the C++ build type is unstated (issue #3 only asks whether CMake Release is right), and the run used one 1 MiB file. The 5.2x measured libstdc++ std::regex against the regex crate, not language codegen; both sides were 2026-02 builds that later received correctness fixes.

## Known shortcomings

- 5.2x claim obsolete: README update of 2026-02-25 says the C++ version is now slightly faster. The measured C++ (GitLab commit fb5e2f81) used libstdc++ std::regex; commit 06fdbc67 (2026-02-15) removed std::regex and fixed a correctness bug, so the win came from the regex library, not the language. C++ flags unstated, bench binaries not committed, 0 stars.
- Correctness bug: parse.rs breaks on the first non-UTF-8 line, so a Latin-1 byte silently truncates DATA plus the footer with no error (confirmed with a std-only test); the CLI can write over its input file; remap_references' parse::&lt;u32&gt;().unwrap() panics on '#' plus digits beyond u32, including inside quoted strings. The benchmarked 2026-02-14 Rust builds predate two geometry-loss fixes (CDSR root 2026-02-15, SHAPE_REPRESENTATION_RELATIONSHIP root 2026-03-01); C++ had the same bugs. LibrePCB #1693: the C++ version is now about 4% faster, so the 5.2x claim is reversed, and output now diverges from C++ master.

## Caveats and trade-offs

Superseded by the README's own update: after the C++ project changed, it is 'now slightly faster again than this Rust codebase', so the 5.2x figure is obsolete. The measured C++ baseline was the 2026-02-05 rewrite (GitLab commit fb5e2f81), which used libstdc++ std::regex for NUM_PATTERN, NAME_PATTERN, REF_PATTERN and UNCERTAINTY_PATTERN; commit 06fdbc67 on 2026-02-15 (the day after issue #3) replaced those regexes with hand-written parsing and also fixed a C++ correctness bug ('Missed an identity element ... led to some breakage in repeated patterns'), so the numbers were taken against baseline code later fixed for correctness. Single 1 MiB input file in a niche format (STEP CAD), hyperfine with 3 warmups; the gap is a std::regex-versus-regex-crate illustration, not a language result. The Rust port was produced with LLM help and the author disclaims correctness beyond the test suite. The original C++ project is on GitLab (sethhillbrand/stepreduce, GPL-3.0-or-later; GitLab reports no detected license object); its issue page carries embedded text addressed to AI agents, which was ignored. [retier] parse.rs breaks on the first non-UTF-8 line, so a Latin-1 byte silently truncates DATA plus the footer with no error; the CLI can overwrite its input; remap_references panics on '#' plus digits beyond u32, including inside quoted strings. The benchmarked 2026-02-14 builds predate two geometry-loss fixes (CDSR root 2026-02-15, SHAPE_REPRESENTATION_RELATIONSHIP root 2026-03-01); C++ had the same bugs. LibrePCB #1693: C++ is now about 4% faster, and output now diverges from C++ master.

GPL-3.0-or-later like the original. Output is verified identical to the C++ program by about 80 generated test files.

## Maintenance

Small single-author port (19 commits, last 2026-03-01, 0 stars, GPL-3.0-or-later, not published on crates.io; issue #2 is open), under evaluation for LibrePCB 2.2.0 (issue #1693 open). Its headline 5.2x is now reversed (C++ about 4% faster), it silently truncates non-UTF-8 input, and its orphan-removal heuristic has needed two geometry-loss fixes since the benchmark.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** README carries a first-party hyperfine run (cpp-baseline 505.4 ms, rs-baseline 145.2 ms, rs-prealloc 97.2 ms, 5.20 +/- 0.10x) on an AMD Ryzen 9 5900X, but the bench/ binaries and build commands are not in the repository and neither side's compiler flags are stated, so it cannot be A; the README's own 2026-02-25 update says the C++ project is now slightly faster.
- **Verifier notes:** Real measurement but against a superseded C++ version; flag as not faster any more (README update 2026-02-25: C++ now slightly faster). Shortcomings: win came from libstdc++ std::regex vs Rust regex crate and hand-written scanning (library, not language), C++ flags unstated and bench binaries not committed, single input file, baseline later fixed for a correctness bug, 0 stars. Not a duplicate.
- **Fields the verifier corrected:** `compiler_and_flags`, `caveats`
- **Shortcomings recorded by:** verifier batch-37 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/dbrgn/stepreduce-rs>
  - <https://github.com/dbrgn/stepreduce-rs/commits>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/Cargo.toml>
  - <https://github.com/dbrgn/stepreduce-rs/tree/main/src>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/src/references.rs>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/src/normalize.rs>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/issues/3>
  - <https://gitlab.com/api/v4/projects/sethhillbrand%2Fstepreduce/issues/3>
  - <https://gitlab.com/api/v4/projects/sethhillbrand%2Fstepreduce>
  - <https://gitlab.com/api/v4/projects/sethhillbrand%2Fstepreduce/repository/commits?per_page=30>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/raw/master/CMakeLists.txt>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/raw/master/stepreduce.cpp>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/raw/fb5e2f8108a3c9ad58962cd4b1fe6600c6b35adb/stepreduce.cpp>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/raw/06fdbc674ded5f0d50cffd993aa475db9eb1eece/stepreduce.cpp>
- **Sources the enricher read:**
  - <https://github.com/dbrgn/stepreduce-rs>
  - <https://github.com/dbrgn/stepreduce-rs/commits>
  - <https://github.com/dbrgn/stepreduce-rs/commits/main>
  - <https://github.com/dbrgn/stepreduce-rs/commit/9114ce6935385e604546a68f04a4f3f31d6b448d>
  - <https://github.com/dbrgn/stepreduce-rs/commit/c3a320e0d6264773cbfbbb427a1bdafd1b556cf2>
  - <https://github.com/dbrgn/stepreduce-rs/issues>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/README.md>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/src/lib.rs>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/src/main.rs>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/src/parse.rs>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/src/deduplicate.rs>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/src/normalize.rs>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/src/find_numbers.rs>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/src/references.rs>
  - <https://raw.githubusercontent.com/dbrgn/stepreduce-rs/HEAD/src/orphans.rs>
  - <https://crates.io/api/v1/crates/stepreduce-rs>
  - <https://crates.io/api/v1/crates/stepreduce>
  - <https://gitlab.com/api/v4/projects/sethhillbrand%2Fstepreduce/issues/3>
  - https://gitlab.com/api/v4/projects/sethhillbrand%2Fstepreduce/issues/3/notes (401)
  - <https://gitlab.com/api/v4/projects/sethhillbrand%2Fstepreduce/repository/commits?per_page=40>
  - <https://gitlab.com/api/v4/projects/sethhillbrand%2Fstepreduce/repository/commits/06fdbc67>
  - <https://gitlab.com/api/v4/projects/sethhillbrand%2Fstepreduce/repository/commits/06fdbc67/diff?per_page=50>
  - <https://gitlab.com/api/v4/projects/sethhillbrand%2Fstepreduce/repository/commits/fb5e2f81>
  - <https://gitlab.com/api/v4/projects/sethhillbrand%2Fstepreduce/repository/tree?per_page=100>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/raw/fb5e2f8108a3c9ad58962cd4b1fe6600c6b35adb/CMakeLists.txt>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/raw/fb5e2f8108a3c9ad58962cd4b1fe6600c6b35adb/CMakePresets.json>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/raw/fb5e2f8108a3c9ad58962cd4b1fe6600c6b35adb/Makefile>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/raw/fb5e2f8108a3c9ad58962cd4b1fe6600c6b35adb/README.md>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/raw/master/CMakeLists.txt>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/raw/master/CMakePresets.json>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/raw/master/Makefile>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/raw/master/README.md>
  - <https://gitlab.com/sethhillbrand/stepreduce/-/raw/master/stepreduce.cpp>
  - <https://github.com/LibrePCB/LibrePCB/issues/1693>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/dbrgn/stepreduce-rs`) · [data/wave14/enrich/raw/github_com_dbrgn_stepreduce_rs.json](../../../data/wave14/enrich/raw/github_com_dbrgn_stepreduce_rs.json) (enrichment confidence 0.75)

</details>
