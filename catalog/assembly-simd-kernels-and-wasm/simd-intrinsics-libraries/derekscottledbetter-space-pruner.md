# space-pruner

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [SIMD intrinsics libraries](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C` · `LicenseRef-public-domain` · 🔴 abandoned

> Two table-free ARM NEON in-place whitespace strippers, built as alternatives to Lemire's scalar and lookup-table NEON despacers; no published timings.

| | |
|---|---|
| **Beats** | scalar despace loop (despacer.h despace) and Lemire's neontbl_despace in the same app |
| **Claimed result** | No numbers anywhere in the repository or README. The README only says the project tests ways to remove whitespace on ARM, based on two Daniel Lemire blog posts, and adds neon_interleaved_despace (the later commits add neon_unzipping_despace). |
| **Workload** | SpacePruner/despacebenchmark.c: remove whitespace (space, LF, CR; about 3% of bytes) from a 32 KiB random buffer refilled before each run, best of 100 runs, printed as nanoseconds per input byte under the label 'ns per operation' by an iOS app (gettimeofday timer with microsecond resolution); scalar despace, neontbl_despace (AArch64 only), neon_interleaved_despace and neon_unzipping_despace are timed; no results are recorded in the repo. |
| **Metric** | throughput |
| **Compiler and flags** | Xcode 8 build for iOS 10.3 or later (README); despacebenchmark.c header comment suggests gcc -std=c99 -O3 for desktop builds; no flags recorded for any run. |
| **Adoption** | 11 stars, 1 fork, 35 commits |
| **Last commit** | 2017-07-20 |
| **Links** | [repository](https://github.com/DerekScottLedbetter/space-pruner) |

## Verdict

Nothing was measured in public: the repository holds an iOS app that times scalar despace, Lemire's AArch64 neontbl_despace and the two new NEON kernels on a 32 KiB random ASCII buffer with about 3% whitespace, but no results, device, compiler flags or screenshots are committed, and the Lemire blog posts that discuss NEON despacing could not be opened here.

## Use it when

- In-place stripping of whitespace and control bytes from ASCII buffers on ARMv7 NEON or AArch64 (phones, Apple silicon, Graviton-class servers) when a 1 MiB lookup table is unwelcome.
- As a reference for table-free NEON stream compaction (bit-isolation or polynomial-multiply index generation) to adapt to other byte filters.
- Buffers of at least a few hundred bytes: the vector loops need 128 bytes (interleaved) or 256 bytes (unzipping) before they run; shorter inputs fall to the scalar tail.
- Codebases that can take public-domain source drops and will run their own benchmark, since the repository gives no numbers.

## Skip it when

- x86 or any non-NEON target: the functions are not even declared without __ARM_NEON; use lemire/despacer, which also has SSE/AVX variants and published cycle counts.
- Non-ASCII (UTF-8) text on Apple platforms or any target where char is signed: the scalar tails delete bytes 0x80-0xFF while the vector body keeps them (see gotchas).
- When only space, LF and CR should go: tabs, NUL and all other control bytes are removed too.
- Anyone needing measured evidence or maintenance: no timings were ever published and the code has been untouched since 2017-07-20.
- Out-of-place use without adaptation: the kernels are written for in-place operation and store 8 bytes at a time past the logical end of the output.

## How it is fast

Both kernels de-interleave 64 bytes with vld4q_u8, compare against 0x20 and pack the keep flags into one byte per 8 input bytes, then turn each flag byte into an 8-lane shuffle index vector computed in registers, so the 1 MiB shufmask table that neontbl_despace indexes with a 16-bit movemask is gone. The interleaved kernel finds set bits by repeated lowest-set-bit isolation (x & (x-1) with vcntq_u8 on the trailing ones); the unzipping kernel splits alternating set bits with a carry-less multiply by all ones (vmulq_p8 prefix XOR) applied three times, reading the last two bit positions with vcntq_u8 and vclzq_u8. Each 8-byte group is then gathered with vtbl1_u8 (or vqtbl1q_u8 on AArch64) and stored with an overlapping 8-byte vst1_u8, advancing the output pointer by the popcount.

## Compared with alternatives

Pick lemire/despacer (Despacer) in nearly every case: it covers x86 and ARM, has published cycle-per-byte results and a maintained repository. Pick space-pruner only when you specifically want a table-free NEON compaction kernel to study or adapt, and test it yourself on non-ASCII input first.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none beyond arm_neon.h; the headers include the Apple SDK header &lt;ConditionalMacros.h&gt;, which must be removed to build outside Xcode |
| **Minimum toolchain** | C99 with clang (Xcode 8 era); relies on clang-specific _Pragma("unroll") (GCC ignores it with a warning) and on clang accepting a uint8x16_t initialiser for a poly8x16_t in the unzipping kernel; the benchmark harness folds a const-sized initialised array, a clang extension |
| **Platforms** | ARMv7 with NEON (vtbl1_u8 path) and AArch64 (vqtbl1q_u8 path in the interleaved kernel); no scalar fallback for other targets |
| **Thread safety** | not documented; both kernels touch only the caller's buffer and no shared state, so concurrent calls on separate buffers should be safe |
| **Drop-in for the baseline** | partial — same signature and in-place contract as despacer's despace(), but NEON-only, and on signed-char targets the tail handles bytes 0x80-0xFF differently from the vector body |

## Gotchas

- Signed-char correctness bug, untested by the harness: the vector body keeps bytes 0x80-0xFF (unsigned vcgtq_u8 compare against 32), but the scalar tail of both kernels does 'const char c = \*source++; if (c &gt; space)', so on Apple arm64 and other signed-char targets any UTF-8 byte in the last 1-127 (interleaved) or 1-255 (unzipping) bytes is deleted. The scalar baseline despace() in despacer.h also uses signed char and deletes every non-ASCII byte there, while Lemire's neontbl_despace tail uses unsigned char. The benchmark cannot see this because fillwithtext() loops 'while (buffer[i] &lt;= 32)', which rejects every negative char, so the test data on iOS is pure 7-bit ASCII.
- Harness timer: gettimeofday with microsecond resolution over a 32 KiB buffer, best of 100 runs, printed under 'ns per operation' though the figure is nanoseconds per input byte; at sub-nanosecond-per-byte speeds one run lasts only tens of microseconds, so each figure carries several percent of quantisation.
- The workload has only about 3% whitespace (1% each of space, LF and CR), far below prose; that keeps the baseline neontbl_despace's 1 MiB table mostly on a few hot entries, so the harness does not exercise the table-cache pressure the table-free kernels are designed to avoid.
- Every vst1_u8 writes a full 8 bytes and advances by the popcount, so the output region needs 8 bytes of slack; in place this stays inside already-consumed input, but a copying variant must allocate extra room. The 2.87 MB bigtable.h defines a non-const, non-static 1 MiB global in a header, so despacer.h can be included in only one translation unit.

## Known shortcomings

- No results recorded anywhere; the benchmark is an iOS-only app with a microsecond timer; public domain stated only in README.txt; abandoned since 2017. Adds its own NEON kernels, so it is not a copy of lemire/despacer.
- Enricher: signed-char bug: the vector bodies keep bytes 0x80-0xFF but the scalar tails of neon_interleaved_despace and neon_unzipping_despace use `const char c` with `c > 32`, so on Apple arm64 they delete non-ASCII bytes in the last 128 or 256 bytes, and the scalar baseline deletes all non-ASCII bytes; the correctness check is blind because the generated text is pure ASCII. Apple-only include, microsecond timer, 'ns per operation' label is actually ns per byte, and 3% whitespace keeps the 1 MiB table hot.

## Caveats and trade-offs

No measurements, so tier D, and the project is not widely referenced (11 stars); kept because it is the closest ARM relative of the already-listed Despacer (lemire/despacer). The code is a benchmark app only: results appear on-device when the user taps Run, and the timer is gettimeofday at microsecond resolution over a 32 KiB buffer, so per-byte figures would be coarse. The licence is the README.txt sentence 'This project and all of its code is public domain.' with no LICENSE file (no patent grant); the benchmark and scalar code are 'Originally written by Daniel Lemire', whose blog-code repository also states a public-domain intent, but copyright notices were removed from the copies (commit 'Added a README, and removed copyright notices.'). The 2017 Lemire blog posts that report NEON despacing timings were not opened (blogs blocked) and two WebSearch queries for them returned nothing usable. Abandoned since 2017-07-20. [retier] Enricher: the scalar tails and the scalar baseline delete non-ASCII bytes on Apple arm64 (signed char compared with 32) while the vector bodies keep them; the generated test text is pure ASCII, so the check never sees the difference.

ARM NEON only (AArch64 and 32-bit variants); Objective-C iOS harness; in-place despacing that returns the new length. Related to lemire/despacer but ARM-specific.

## Maintenance

Abandoned since 2017-07-20 after a two-week burst of 35 commits; the README declares the project public domain (no LICENSE file, no patent grant, copyright notices on the Lemire-derived code removed), and the two kernels are small enough to vendor once the Apple header and the signed-char tail are fixed.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification D, tier now D.
- **Tier reason:** benchmark_url is null and the repository (README.txt plus SpacePruner/despacebenchmark.c) contains benchmark code against the scalar despace and Lemire's neontbl_despace but records no results anywhere; one search for the Lemire posts' mention of this work found nothing, so tier D.
- **Verifier notes:** No numbers anywhere; confirmed at D and kept per the keep-and-document rule (not a reject). Shortcomings: no recorded results, iOS-only harness with a microsecond timer, README-only public-domain statement with no patent grant, abandoned 2017. Not a duplicate: it adds its own NEON kernels on top of Lemire's despacer code.
- **Fields the verifier corrected:** `workload`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-127 (wave 13 seed pass, 2026-10-13); enricher (seed pass, 2026-10-13)
- **Pages the verifier opened:**
  - <https://github.com/DerekScottLedbetter/space-pruner>
  - <https://github.com/DerekScottLedbetter/space-pruner/commits>
  - <https://raw.githubusercontent.com/DerekScottLedbetter/space-pruner/HEAD/README.txt>
  - <https://raw.githubusercontent.com/DerekScottLedbetter/space-pruner/HEAD/SpacePruner/despacebenchmark.c>
- **Sources the enricher read:**
  - <https://raw.githubusercontent.com/DerekScottLedbetter/space-pruner/HEAD/README.txt>
  - <https://raw.githubusercontent.com/DerekScottLedbetter/space-pruner/HEAD/SpacePruner/despacebenchmark.c>
  - <https://github.com/DerekScottLedbetter/space-pruner/tree/master/SpacePruner>
  - <https://raw.githubusercontent.com/DerekScottLedbetter/space-pruner/HEAD/SpacePruner/despacer.h>
  - <https://raw.githubusercontent.com/DerekScottLedbetter/space-pruner/HEAD/SpacePruner/interleaved_despacer.c>
  - <https://raw.githubusercontent.com/DerekScottLedbetter/space-pruner/HEAD/SpacePruner/interleaved_despacer.h>
  - <https://raw.githubusercontent.com/DerekScottLedbetter/space-pruner/HEAD/SpacePruner/unzipping_despacer.c>
  - <https://raw.githubusercontent.com/DerekScottLedbetter/space-pruner/HEAD/SpacePruner/unzipping_despacer.h>
  - <https://raw.githubusercontent.com/DerekScottLedbetter/space-pruner/HEAD/SpacePruner/ViewController.m>
  - <https://raw.githubusercontent.com/DerekScottLedbetter/space-pruner/HEAD/SpacePruner/bigtable.h>
  - <https://github.com/DerekScottLedbetter/space-pruner/commits/master>
  - <https://raw.githubusercontent.com/lemire/Code-used-on-Daniel-Lemire-s-blog/master/2017/07/10/README.md>
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/derekscottledbetter/space-pruner`) · [data/wave13/enrich/raw/github_com_derekscottledbetter_space_pruner.json](../../../data/wave13/enrich/raw/github_com_derekscottledbetter_space_pruner.json) (enrichment confidence 0.6)

</details>
