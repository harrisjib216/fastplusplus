# zigmark (Zig CommonMark parser and renderer)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier D** (directional, no numbers) · Study only · `Zig` · `PolyForm-Noncommercial-1.0.0` · 🟢 active

> Zig CommonMark+GFM parser and HTML/Typst renderer; README shows it ahead of cmark only through a shell-wrapped baseline.

| | |
|---|---|
| **Beats** | cmark and cmark-gfm (C); the same table also lists lowdown and discount (C) and pandoc (Haskell). |
| **Claimed result** | README Performance table (last updated 2026-06-04, input README.md 27 KB, hyperfine -N, 50 warm-ups, 500 runs), mean ms: lowdown 2.2 +/- 0.8, zigmark ReleaseFast 2.4 +/- 1.0, discount 2.7 +/- 1.2, zigmark ReleaseSmall 2.9 +/- 0.7, zigmark ReleaseSafe 4.4 +/- 1.0, cmark 5.3 +/- 1.4, cmark-gfm 5.6 +/- 1.2; pandoc 185.4 +/- 32.2 (separate 20-run hyperfine call). zigmark ReleaseFast vs cmark about 2.2x and vs cmark-gfm about 2.3x, ReleaseSafe vs cmark about 1.2x (derived from page data), but the cmark and cmark-gfm rows include an extra /bin/sh wrapper process that the zigmark rows do not (see caveats). lowdown (C) is faster than every zigmark build and discount (C) is within one standard deviation of ReleaseFast. Peak RSS (GNU time -v, one run each): zigmark ReleaseSmall 1952 KB, discount 2124 KB, zigmark ReleaseFast 2412 KB, lowdown 2988 KB, zigmark ReleaseSafe 3116 KB, cmark-gfm 4300 KB, cmark 4336 KB, pandoc 129416 KB; the cmark and cmark-gfm RSS figures are also taken through the shell wrapper, so they include the shell's footprint. |
| **Workload** | Convert the repository's own 27 KB README.md from Markdown to HTML on the command line, one process per run (the bench app uses the CommonMark spec.txt only when it is cached, and the published table says README.md); hyperfine -N mean wall time per process over 500 runs after 50 warm-ups, plus one-run peak RSS via GNU time -v (`nix run .#bench`, defined in flake.nix). |
| **Metric** | latency |
| **Compiler and flags** | zigmark: Zig 0.16.0, built by the flake's mkZigmark helper with -Doptimize=ReleaseFast, ReleaseSmall and ReleaseSafe. cmark, cmark-gfm, discount, lowdown and pandoc are the nixpkgs packages pulled in as runtimeInputs of the `bench` app in flake.nix; their versions and build flags are not stated. Harness: hyperfine -N --warmup 50 --runs 500; cmark and cmark-gfm are invoked through a generated `#!/bin/sh` script that execs them with stdout redirected to /dev/null, while zigmark, discount and lowdown are invoked directly with -o /dev/null. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | not stated |
| **Adoption** | 6 stars |
| **Last commit** | 2026-08-07 |
| **Links** | [repository](https://github.com/sc2in/zigmark) · [benchmark](https://raw.githubusercontent.com/sc2in/zigmark/HEAD/README.md) |

## Verdict

One process per run converting the repo's own 27 KB README.md to HTML, hyperfine -N mean over 500 runs on an unstated machine: zigmark ReleaseFast 2.4 ms against cmark 5.3 ms and cmark-gfm 5.6 ms (nixpkgs builds, versions unstated), but the cmark rows include an extra /bin/sh process; the directly spawned C tools lowdown (2.2 ms) and discount (2.7 ms) tie or beat zigmark, so no valid win over C is shown.

## Use it when

- Zig projects that want an in-process CommonMark+GFM parser with a typed AST, block mutation and frontmatter editing in one module.
- Markdown-to-Typst/PDF pipelines (eisvogel-style preamble driven by frontmatter, mermaid fences rendered to SVG through the lazy pozeiden dependency).
- Noncommercial or internal tooling that wants a small static CLI (about 2 MB peak RSS on a 27 KB file) or a WASM build of about 81 KiB.
- Doc-site tooling that needs to query or rewrite sections of many Markdown files (the Library query API, --set-block, --section-start/--section-end).

## Skip it when

- Commercial products or paid client work: PolyForm Noncommercial 1.0.0 forbids it without a separate licence from SC2 (solo practitioners using it as a tool are exempted in the README).
- When raw conversion speed is the goal: on the repo's own unwrapped comparison lowdown (2.2 ms) beats every zigmark build and discount (2.7 ms) is within one standard deviation of ReleaseFast (2.4 ms); no throughput test on large inputs exists.
- Untrusted input without limits: SECURITY.md documents O(n^2) worst-case behaviour of the inline scanner on unmatched brackets, bounded only by the input cap, whereas cmark is built to stay linear on pathological input.
- Inputs over 16 MiB: Parser.max_input_bytes defaults to 16 MiB and the CLI uses the default, so larger files fail with error.InputTooLarge.
- Toolchains other than Zig 0.16.0 or later; 0.x API that has changed across 11 minor releases since 2025.

## How it is fast

Two passes: a first scan of every line collects link reference definitions into a hash map, then a block pass (mecha parser combinators plus hand-written line classifiers over a pre-split line array) and a hand-written inline state machine implement the CommonMark delimiter algorithm. Plain-text runs inside inlines are skipped with a `@Vector` byte-compare scan for the special characters (`*_~[!`&lt;\` and newline, plus `@` under GFM), with a lookup-table scalar tail. Renderers stream into an 8 KiB buffered writer instead of building the output string. Nothing in the code points to a structural advantage over cmark: the README's lead over cmark comes from a harness asymmetry (see gotchas).

## Compared with alternatives

rushdown (Rust) is the closer CommonMark sibling and its make-bench numbers beat cmark in-process without a wrapped baseline; pick zigmark only when you need a Zig-native or C-ABI library with Typst output and frontmatter/AST editing, and your use is noncommercial.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | mecha, zig-clap, mvzr, tomlz and zig-yaml (SC2 forks for the last two); pozeiden (lazy, for mermaid SVG in the CLI/WASM; a no-op fallback when used as a library); commonmark-spec and cmark-gfm are fetched only for the spec tests. |
| **Minimum toolchain** | Zig 0.16.0 (minimum_zig_version in build.zig.zon) |
| **Platforms** | any Zig target; CI on x86_64-linux and aarch64-linux; wasm32 build; SIMD scan falls back to scalar where no vector length is suggested |
| **Thread safety** | not documented (Parser is a plain value struct and all output is caller-owned; pozeiden made its mermaid rendering thread-safe in v0.2.0) |
| **Drop-in for the baseline** | partial — the CLI takes a file and writes HTML like cmark, but adds -o, enables GFM extensions by default, and the C ABI differs from cmark's cmark_markdown_to_html/node API |

## Gotchas

- Harness flaw behind the headline: flake.nix's bench app runs cmark and cmark-gfm through a generated `#!/bin/sh` wrapper (`exec cmark "$@" > /dev/null`) while zigmark, lowdown and discount are spawned directly under `hyperfine -N`, so every cmark run pays an extra shell start on a 2-5 ms start-up-dominated workload (hyperfine's `--output=null` would have made it symmetric), and the cmark peak-RSS rows include the shell. The work also differs: the zigmark CLI parses with GFM extensions on and a mermaid hook, while plain `cmark`/`cmark-gfm` (no -e flags) render CommonMark only.
- The README table is stale: it is dated 2026-06-04 (the v0.7.0 release that added the bench app) and says README.md was 27 KB, but README.md is now about 33 KB and the current bench app also writes a 'mermaid-heavy input' table that the README lacks, so the numbers predate releases 0.8.0 to 0.11.1 and the current harness. No CPU or baseline versions are given.
- The C ABI (`zigmark_parse`, `zigmark_render_*` in src/root.zig) allocates every AST node and string with `std.heap.page_allocator`, i.e. a page-granular mmap/munmap per allocation, so C callers get a much slower and more memory-hungry path than the CLI's general-purpose allocator; `zigmark_free_string` recovers the length by scanning for the NUL terminator.
- The separate `nix run .#benchmark` app (benchmark.md) is a zigmark-only self-comparison whose command `./zig-out/bin/zigmark ./Readme.md > /dev/null` runs under hyperfine -N, so `>` and `/dev/null` are passed as arguments rather than a redirect, and the file name differs in case from README.md.

## Known shortcomings

- Crippled baseline: the flake.nix bench runs cmark and cmark-gfm through a /bin/sh wrapper (exec cmark "\$@" &gt; /dev/null, about 1 ms per spawn on 2-5 ms runs, and the cmark RSS rows include the shell) while zigmark, lowdown and discount are spawned directly; unwrapped C lowdown (2.2 ms) beats zigmark (2.4 ms) and discount (2.7 ms) is within noise. PolyForm Noncommercial license, reference only.
- Shell-wrapper flaw confirmed in flake.nix: cmark and cmark-gfm run through /bin/sh while zigmark runs directly. Workloads differ too: zigmark runs with GFM and the mermaid hook on against plain cmark without -e. The README table is stale (dated 2026-06-04, v0.7.0, 27 KB input while the README is now about 33 KB, and it lacks the mermaid table the current bench app writes). The C ABI (src/root.zig zigmark_parse) uses std.heap.page_allocator, so each allocation is a page-sized mmap; the inline scanner is O(n^2) (SECURITY.md); 16 MiB default input cap. lowdown still beats every zigmark build.

## Caveats and trade-offs

Harness asymmetry: in flake.nix the cmark and cmark-gfm commands are run through a generated /bin/sh wrapper (`exec cmark "$@" > /dev/null`) because cmark has no -o option, while zigmark, lowdown and discount are spawned directly by hyperfine -N; every baseline run therefore pays an extra shell start-up (about 1 ms per spawn with dash in the verifier's container; NixOS's /bin/sh is bash, which is heavier), on runs that take 2 to 5 ms in total, and hyperfine's --output=null would have avoided it. The same wrapper means the cmark and cmark-gfm peak-RSS figures are the maximum of the shell and cmark, since Linux carries the pre-exec high-water mark into ru_maxrss. One 27 KB input, so process times are dominated by start-up and file I/O; no CPU or machine stated; baseline versions and flags not stated (nixpkgs packages). C tools measured without the wrapper (lowdown 2.2 ms, discount 2.7 ms) tie or beat zigmark ReleaseFast (2.4 +/- 1.0 ms). Different parser design (mecha parser combinators) from cmark, so this is not a language-level comparison. Benchmark output is auto-written into the README by the repo's own bench app. The PolyForm Noncommercial 1.0.0 licence forbids commercial use, so the code is reference-only. [retier] Workloads differ: zigmark runs with GFM and the mermaid hook on against plain cmark without -e. The README table is stale (2026-06-04, v0.7.0, 27 KB input while the README is now about 33 KB). The C ABI uses std.heap.page_allocator (one page-sized mmap per allocation); the inline scanner is O(n^2); 16 MiB default input cap.

Two-pass parser built on the mecha parser-combinator library; passes the CommonMark spec tests (652) and 24 GFM extension tests per README; also offers Typst and Markdown renderers, frontmatter handling and a C ABI. Noncommercial licence (not OSI-approved).

## Maintenance

Active (162 commits, v0.11.1 on 2026-08-07, 3 open issues, two of them Zig 0.16 migration bugs in the terminal renderer and spec-runner timing) and passes all 652 CommonMark and 24 GFM spec tests, but PolyForm Noncommercial licensing makes it reference-only for commercial users and the only speed evidence comes from a harness that shell-wraps the cmark baselines.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** The README table (written by the flake.nix `bench` app) does compare against cmark and cmark-gfm, but in flake.nix only the cmark and cmark-gfm commands run through a generated /bin/sh wrapper script (`exec cmark "$@" > /dev/null`) while zigmark, lowdown and discount are spawned directly by `hyperfine -N`, so each baseline run pays an extra shell start-up on a 2-5 ms start-up-dominated workload; the C tools measured without the wrapper (lowdown 2.2 ms, discount 2.7 ms) tie or beat zigmark ReleaseFast (2.4 ms), so no valid measured win over C remains (hop start-up-dominated and AssemblyScript crippled-baseline precedents). Even taken at face value it would be C: no CPU, no baseline build flags.
- **Verifier notes:** Numbers on the page match the record, but flake.nix's bench app wraps only cmark and cmark-gfm in a /bin/sh exec script, so their time and RSS rows include an extra shell process on a start-up-dominated 2-5 ms workload; the unwrapped C tools (lowdown, discount) show zigmark is not faster than C. Downgraded C to D under the hop and crippled-baseline precedents; metadata (PolyForm-Noncommercial-1.0.0, 6 stars, last commit 2026-08-07, active) checked and unchanged. If the orchestrator prefers to keep the numbers, the fallback is tier C with this harness flaw as the shortcoming.
- **Fields the verifier corrected:** `claimed_speedup`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-64 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/flake.nix>
  - <https://github.com/sc2in/zigmark>
  - <https://github.com/sc2in/zigmark/commits>
- **Sources the enricher read:**
  - <https://github.com/sc2in/zigmark>
  - <https://github.com/sc2in/zigmark/tree/main/src>
  - <https://github.com/sc2in/zigmark/tree/main/src/markdown>
  - <https://github.com/sc2in/zigmark/issues>
  - <https://github.com/sc2in/zigmark/commits/main>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/README.md>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/flake.nix>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/build.zig>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/benchmark.md>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/SECURITY.md>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/src/main.zig>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/src/root.zig>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/src/noop_mermaid.zig>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/src/markdown/parser.zig>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/src/markdown/inline.zig>
  - <https://raw.githubusercontent.com/sc2in/zigmark/HEAD/src/markdown/combinators.zig>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/sc2in/zigmark`) · [data/wave14/enrich/raw/github_com_sc2in_zigmark.json](../../../data/wave14/enrich/raw/github_com_sc2in_zigmark.json) (enrichment confidence 0.75)

</details>
