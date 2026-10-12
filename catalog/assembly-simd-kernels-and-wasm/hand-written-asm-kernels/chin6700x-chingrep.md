# chingrep

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [Hand-written assembly kernels](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Assembly (hand-written ARM64 GNU assembler) and C (x86_64 AVX2 intrinsics)` · `MIT` · 🟢 active

> Literal-only, grep-style recursive search tool in C with ARM64 NEON assembly kernels; claims 6.7x over ripgrep on the author's private tree.

| | |
|---|---|
| **Beats** | ripgrep 15.2.0 (rev e89fff89ac), per arena/ARENA_REPORT.md |
| **Claimed result** | Total arena time 1,870.9 ms (cg) vs 12,470.7 ms (rg), 6.7x faster overall; cg wins 21 of 22 scenarios; literal search 87.3 vs 641.0 ms (7.3x); exclude-dir 79.9 vs 670.3 ms (8.4x); include \*.c 27.9 vs 37.9 ms (1.4x); piped stdin 3.6 vs 3.5 ms (rg wins). |
| **Workload** | arena/run-arena.sh: 22 scenarios (literal, -i, -w, -rniw, -c, -ci, -cw, -l, -li, -lw, -m 1/5/10, include \*.js / \*.c globs, exclude-dir, hit-frequency classes, nonexistent needle, stdin) over the author's 'treesource' workspace (17,000+ files, not public); one chingrep-only warm-up, then best of 3 per tool, each run timed with Python perf_counter around subprocess.run(shell=True). The report was generated 2026-10-05. |
| **Metric** | latency |
| **Hardware** | Apple Silicon ARM64 (chip model not stated) |
| **Compiler and flags** | Makefile: CC ?= clang, CFLAGS -O3 -Wall -Wextra -pthread -fomit-frame-pointer; ARM64 .s files assembled through \$(CC) with -O3; compiler version not stated |
| **Adoption** | 0 stars |
| **Last commit** | 2026-10-08 |
| **Links** | [repository](https://github.com/chin6700x/chingrep) · [benchmark](https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/README.md) |

## Verdict

arena/run-arena.sh timed chingrep 1.0.0 (clang -O3, ARM64 NEON build) against ripgrep 15.2.0 on an unnamed Apple Silicon Mac over the author's private 17,000-file 'treesource' folder, best of 3 runs each via Python perf_counter around subprocess.run, with a warm-up only for chingrep: 1,870.9 ms vs 12,470.7 ms summed over 22 scenarios (6.7x), around 87 ms vs 640 ms for unfiltered literal searches, 27.9 vs 37.9 ms with a \*.c filter and a loss on stdin (3.6 vs 3.5 ms). Because the two tools almost certainly searched different file sets (ripgrep's unfiltered time stays near 640 ms regardless of hit count while its \*.c run takes 38 ms), the ratio mostly measures what each tool chooses to skip, not search speed.

## Use it when

- Reading or borrowing a small, MIT-licensed example of a NEON first/last-byte substring filter, NEON memchr and a NEON newline counter on Apple Silicon.
- Personal ad-hoc literal searches on macOS/Apple Silicon over JavaScript/web project trees where skipping node_modules, dist and build is what you want anyway.
- Benchmarking experiments where you deliberately control both tools' file sets (for example cg --no-ignore against rg -uu, or both given the same explicit file list).

## Skip it when

- Any search that needs regular expressions, inverted matches, context lines, Unicode case folding or exact .gitignore semantics; ripgrep provides all of these.
- Trees with source directories or files named build, dist, target or coverage (Chromium's top-level build/, many CMake and Bazel layouts): cg silently skips them unless --no-ignore, which also disables .gitignore handling.
- Linux: src/core/pool.c includes &lt;sys/sysctl.h&gt; and calls sysctlbyname unconditionally (the header was removed in glibc 2.32 and sysctlbyname is BSD/macOS-only), and the ARM64 .s files export Mach-O underscore symbols, so the README's Linux support looks unbuilt and untested.
- Case-insensitive searches on ARM64: arm64_search_literal_icase is a plain scalar byte-at-a-time O(n\*m) loop with no NEON at all.
- x86_64 machines without AVX2: the Makefile builds the x86 target with -mavx2 -mfma and the 'dispatcher' is compile-time only, so the binary has no runtime fallback.

## How it is fast

The case-sensitive ARM64 kernel (src/asm/simd_arm64.s) compares the needle's first and last bytes against 16-byte NEON windows and AND-s the masks, verifying candidates byte by byte; memchr, the 512-byte NUL probe and the newline counter are 64-byte unrolled NEON. On x86_64 the same first/last-byte filter is AVX2 intrinsics in C (Mula's generic SIMD substring idea). Files are mmap-ed with MADV_SEQUENTIAL/MADV_WILLNEED, the walker uses readdir d_type instead of lstat, and the pool sizes itself to Apple P-cores via sysctl hw.perflevel0.physicalcpu. Most of the measured gap, however, plausibly comes from searching fewer files: the walker always skips any file or directory named .git, node_modules, dist, build, target, coverage, .next, .nuxt, .idea, .vscode or .DS_Store.

## Compared with alternatives

Like oxsv (SIMD C CLI that claims a large lead over a Rust tool, xsv), chingrep is best treated as readable sample code rather than a replacement; pick it over asmlib's strstr/memmem when you specifically want an AArch64 NEON assembly first/last-byte filter, and pick ripgrep itself for real searches.

## Integration

| | |
|---|---|
| **Form** | static binary built with make (CLI tool; no library API) |
| **Dependencies** | none beyond libc and pthreads (macOS sysctlbyname required by pool.c) |
| **Minimum toolchain** | clang or gcc with GNU assembler syntax for AArch64; Makefile defaults to clang -O3; no version stated |
| **Platforms** | macOS on Apple Silicon (tested by the author); x86_64 requires AVX2 at build and run time; Linux builds likely fail (sys/sysctl.h, sysctlbyname, Mach-O symbol names) |
| **Thread safety** | Process-level tool; one shared output buffer behind a mutex, workers pull paths from a mutex/condvar queue of 65,536 slots |
| **Drop-in for the baseline** | partial — accepts a grep-like subset of flags for literal patterns, but needs -r where rg recurses by default, has no regex, and applies different ignore rules (hard-coded name skips, no hidden-file skipping, no negation rules) |

## Gotchas

- Line-number bug found in this enrichment: src/asm/newline_count.s accumulates up to 64 iterations x 4 vectors = 256 hits per 8-bit lane, one more than a byte holds, so a lane wraps to 0 whenever all 256 of its positions in a 4 KiB block are newlines. Emulating the kernel, a file of 1,000 lines of 16 bytes counts 232 newlines and 5,000 blank lines count 904, so -n (on by default) prints wrong line numbers for runs of blank lines or fixed-width lines whose length divides 16. The comment says the block size was chosen to prevent exactly this overflow; 63 iterations would.
- Unequal work in the arena: cg skips the hard-coded directory names above plus anything matched by any .gitignore (even outside a git repository) and ignores '!' negation rules, while rg skips hidden files that cg searches and honours .gitignore only inside git repositories. Scenario 16 also compares cg --exclude-dir=test, which prunes every directory named test at any depth, with rg -g '!test/\*\*', an anchored glob that at most excludes a top-level test directory. File sets and match counts were never compared.
- The .gitignore parser matches patterns against the bare name or the path relative to the search root, not relative to the .gitignore's own directory, so leading-slash rules ('/build') never match, path rules in nested .gitignore files misfire, lines longer than 255 bytes are split into separate rules, and rules past 512 are dropped silently.
- Several README claims do not match the code: the literal kernel probes 16 bytes per step, not 64; the printer is one shared buffer, not thread-local; the reader still calls fstat on every file; and the 'up to 40x' tagline is not supported by any published row (maximum 8.4x).

## Known shortcomings

- Baseline ripgrep 15.2.0, chip model unstated, workspace private; likely unequal file sets (cg hard-codes skips for node_modules, dist, build, target, coverage that rg does not apply: rg 37.9 ms with a \*.c glob vs about 640 ms unfiltered); the '40x' tagline is unsupported (table max 8.4x); the make-bench script times an undefined \$cg_cmd while the README table comes from arena/run-arena.sh.
- Enricher: line-number bug in src/asm/newline_count.s (64 iterations x 4 vectors = 256 hits per 8-bit lane, so a lane wraps to 0: 1,000 lines of 16 bytes counted as 232, 5,000 blank lines as 904; -n is on by default); the arena does unequal work (hard-coded skips of build/dist/target/node_modules including files, hidden files searched, no '!' negation; cg --exclude-dir=test vs an anchored rg -g '!test/\*\*'); the ARM64 -i kernel is scalar O(n\*m); pool.c needs sys/sysctl.h so the Linux build likely fails; x86 build hard-requires AVX2.

## Caveats and trade-offs

Likely unequal work: chingrep hard-codes ignores for .git, node_modules, dist, build, target, coverage, .next, .nuxt, .idea, .vscode and .DS_Store in src/core/gitignore.c, while ripgrep skips such directories only when a .gitignore excludes them (and honours .gitignore only inside git repositories); chingrep's own .gitignore parser drops negation rules and matches names only. The pattern of results points the same way: ripgrep takes 37.9 ms with -g '\*.c' (full traversal) but about 640 ms for every unfiltered search, while chingrep stays near 87 ms. File sets and match counts were not compared. The tagline says 4x-40x faster, but the published table tops out at 8.4x (6.7x overall) and ripgrep wins the stdin case. Single run on an unnamed Apple Silicon chip; the cache warm-up runs only chingrep. The secondary test/benchmark.sh (make bench) times an undefined \$cg_cmd, so its chingrep column times an empty command; the README table comes from arena/run-arena.sh, which does not have this bug. Only the ARM64 path is hand-written assembly (src/asm/simd_arm64.s, binary_probe.s, newline_count.s); x86_64 uses AVX2 intrinsics in C. The asm symbols carry Mach-O leading underscores, so a Linux aarch64 build may fail to link (not tested). New repo: 0 stars, 8 commits.

Hand-written assembly only on ARM64 (src/asm/simd_arm64.s); the x86_64 path is AVX2 intrinsics in C and a portable C fallback exists.

## Maintenance

Brand-new single-author repo (8 commits between 2026-10-05 and 2026-10-08, 0 stars, no issues, no releases), MIT-licensed and small enough to read in an hour, but macOS-only in practice and with a line-numbering bug, so treat it as reference code rather than a ripgrep replacement.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party 22-scenario table generated by the public arena/run-arena.sh (Makefile: clang -O3) against ripgrep 15.2.0, but the CPU is only 'Apple Silicon' with no chip model, the 17,000-file 'treesource' workspace is not public, and the two tools very likely searched different file sets, so C.
- **Verifier notes:** Table numbers match the README and arena/ARENA_REPORT.md (ripgrep 15.2.0). Shortcomings to record: probable unequal file sets (hard-coded directory skips that ripgrep does not apply), the 40x tagline is unsupported (max 8.4x), the chip model is unstated and the workspace is private, and the make-bench script times an empty command for cg. The evidence is weak but I could not prove it invalid, so I did not reject it. MIT, last commit 2026-10-08, 0 stars confirmed.
- **Fields the verifier corrected:** `baseline`, `compiler_and_flags`, `workload`, `caveats`
- **Shortcomings recorded by:** verifier batch-31 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/README.md>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/arena/run-arena.sh>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/arena/README.md>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/arena/ARENA_REPORT.md>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/test/benchmark.sh>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/Makefile>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/core/walker.c>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/core/gitignore.c>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/asm/dispatcher.c>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/asm/simd_arm64.s>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/LICENSE>
  - <https://github.com/chin6700x/chingrep>
  - <https://github.com/chin6700x/chingrep/commits>
- **Sources the enricher read:**
  - <https://github.com/chin6700x/chingrep>
  - <https://github.com/chin6700x/chingrep/commits>
  - <https://github.com/chin6700x/chingrep/issues>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/README.md>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/arena/run-arena.sh>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/arena/README.md>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/arena/ARENA_REPORT.md>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/test/benchmark.sh>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/test/run-tests.sh>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/Makefile>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/LICENSE>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/.gitignore>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/main.c>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/core/walker.c>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/core/walker.h>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/core/gitignore.c>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/core/gitignore.h>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/core/pool.c>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/core/pool.h>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/core/mmap_reader.c>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/core/mmap_reader.h>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/output/printer.c>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/output/printer.h>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/asm/dispatcher.c>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/asm/simd_engine.h>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/asm/simd_arm64.s>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/asm/binary_probe.s>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/asm/newline_count.s>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/asm/simd_x86_avx2.c>
  - <https://raw.githubusercontent.com/chin6700x/chingrep/HEAD/src/asm/simd_portable.c>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/chin6700x/chingrep`) · [data/wave13/enrich/raw/github_com_chin6700x_chingrep.json](../../../data/wave13/enrich/raw/github_com_chin6700x_chingrep.json) (enrichment confidence 0.75)

</details>
