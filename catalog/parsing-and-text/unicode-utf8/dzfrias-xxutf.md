# xxUTF

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `MIT` · 🟢 active

> Allocation-free C library for Unicode NFD/NFC/NFKD/NFKC and case folding; ARM NEON NFD runs about 3-4.5x ICU4C on non-ASCII UTF-8.

| | |
|---|---|
| **Beats** | ICU4C (unorm2 NFD normalization on UTF-8 input; also compared for NFC, NFKD, NFKC and case folding per README) |
| **Claimed result** | README claims 'the fastest open source implementations of the supported algorithms' and shows one bar chart, doc/neon_utf8_nfd.png (NFD on UTF-8, ARM NEON, GB/s). Values measured from bar pixel heights (derived from page data; 1 pixel = 0.049 GB/s on the 0-35 axis, so each value is +/-0.05 GB/s and the small ICU bars carry 10-20% uncertainty): Arabic 1.91 vs 0.54 GB/s (about 3.5x), Japanese 2.69 vs 0.78 (3.4x), Chinese 4.06 vs 1.03 (4.0x), Hindi 2.59 vs 0.68 (3.8x), Russian 2.44 vs 0.54 (4.5x), Hebrew 2.35 vs 0.64 (3.7x), Korean 0.78 vs 0.24 (3.2x), Latin 34.85 vs 0.34 (about 100x) for xxUTF vs ICU4C. Latin.txt is pure-ASCII lorem ipsum (already NFD), so the Latin bar measures an ASCII pass-through against ICU's UTF-8 to UTF-16 to UTF-8 round trip. |
| **Workload** | NFD normalization of UTF-8 text from eight real-text files in bin/common/inputs (Arabic, Chinese, Hebrew, Hindi, Japanese, Korean, Latin, Russian; e.g. Latin.txt 86,940 bytes pure ASCII, Arabic.txt 81,685 bytes, Korean.txt 66,600 bytes). bin/benchmark/benchmark.zig feeds each file in 4096-byte chunks (trimmed to code-point boundaries), times each chunk with the awake clock and sums per pass, 1000 timed passes after 50 warm-up passes, and reports mean throughput in GiB/s labelled GB/s. The ICU side (IcuNormalizerUtf8) runs u_strFromUTF8, unorm2_normalize with the NFD instance and u_strToUTF8 per chunk into stack buffers; xxUTF works on UTF-8 directly. The README's link to /benchmarks/inputs is stale. |
| **Metric** | throughput |
| **Hardware** | Unnamed 'machine supporting ARM NEON'; CPU model not stated |
| **Compiler and flags** | Zig 0.16.0 build system: 'zig build bench' compiles the xxUTF C amalgamation with ReleaseFast (forced to ReleaseFast if the build mode is Debug), -Wall -Wextra ... -Werror and -DXXUTF_IMPLEMENTATION_NEON=1 on NEON targets (build.zig); ICU4C is linked dynamically as the system icu-uc library, version and build flags not stated. |
| **Adoption** | 15 stars |
| **Last commit** | 2026-07-11 |
| **Links** | [repository](https://github.com/dzfrias/xxUTF) · [benchmark](https://github.com/dzfrias/xxUTF) |

## Verdict

A first-party README bar chart (UTF-8 NFD, unnamed ARM NEON machine, Zig 0.16.0 ReleaseFast build, system ICU4C of unstated version) shows about 0.78-4.1 GB/s for xxUTF vs 0.24-1.03 GB/s for ICU4C on seven non-ASCII language files (3.2-4.5x) and about 35 vs 0.34 GB/s on pure-ASCII Latin text. Values are read from bar heights. ICU is timed per 4 KiB chunk including UTF-8 to UTF-16 to UTF-8 conversion around unorm2_normalize, while xxUTF works on UTF-8 directly.

## Use it when

- Normalizing or case-folding large volumes of already-validated UTF-8 on ARM64 (Apple Silicon, Graviton, phones), for example search-index or dedup pipelines doing NFD/NFKC plus case folding before comparison.
- Mostly-ASCII text where you want an almost free pass-through: the ASCII fast path copies 63-byte blocks, and the README chart shows about 35 GB/s on pure-ASCII Latin text.
- Embedded, kernel or WASM-style environments that cannot allocate or link libc and need standard-conformant normalization (outputs are fuzzed against ICU4C).
- Streaming normalization over chunked input, using the find_first/last_stable APIs (the xxu tool shows the pattern).

## Skip it when

- x86-64 servers when you need proven speed: there is no SSE/AVX path yet, and the README's 'fastest even in scalar mode' claim has no published scalar or x86 numbers.
- Untrusted or possibly invalid input without a separate validation pass (e.g. simdutf validate_utf8): the API assumes valid encoding and 'cannot fail'.
- When you need ICU features beyond NFx and default case folding: Turkic or locale-specific folding, collation, segmentation or a UTF-16 UChar interface.
- Production code with strict security review requirements: the README calls it alpha with a security review still pending. It has 15 stars and one author, and the NEON ASCII fast path shipped with bugs that a follow-up commit (5d54cc2) fixed the same day.
- MSVC builds: the code uses GCC/Clang builtins and attributes (__builtin_expect, __builtin_ctzll, __attribute__((always_inline))).

## How it is fast

It works on UTF-8 or UTF-16 directly instead of converting to UTF-16 as ICU's C API does. The NEON path builds a 64-bit code-point boundary mask per 64-byte block, copies all-ASCII blocks 63 bytes at a time, and otherwise decodes 4-8 code points per step with simdutf-derived shuffles. It looks up decomposition data in a two-level trie with vector table lookups and checks canonical-combining-class order in registers, falling back to a scalar sort only when marks are out of order. Hangul syllables are decomposed arithmetically and branch-free. Other targets run the scalar implementation.

## Compared with alternatives

Pick xxUTF over libutf (brazilofmux/utf) or unicode-transforms when the job is only normalization or case folding on ARM64 and you want an allocation-free single-file C drop. Choose libutf if you also need grapheme breaks or collation, and stay on ICU, or watch simdutf PR #999 (the same author's normalization work with AVX-512 and NEON), if you need x86 SIMD.

## Integration

| | |
|---|---|
| **Form** | source-drop (single-file amalgamation .c plus xxutf.h from the releases page) or static lib (zig build produces libxxutf.a) |
| **Dependencies** | none at run time (no libc, no allocation); building from source needs Zig 0.16.0 and Python (gen/gen.py generates the Unicode tables); the benchmark and fuzzer need ICU4C |
| **Minimum toolchain** | C compiler with GCC/Clang builtins (built by Zig's clang with -Wall -Wextra -Wc++-compat -Werror); header has extern "C" guards for C++; Zig 0.16.0 to build from source |
| **Platforms** | aarch64 with NEON (SIMD path, chosen at build time via XXUTF_IMPLEMENTATION_NEON); any other target uses the scalar path (no x86 SIMD yet) |
| **Thread safety** | not documented; the functions take caller buffers, never allocate and read only constant tables, so concurrent calls on separate buffers look safe (inferred from the API and source) |
| **Drop-in for the baseline** | partial — same normalization and default case-fold results as ICU4C (the fuzzer compares outputs), but a different C API on UTF-8/UTF-16 bytes with caller-sized buffers and no error reporting |

## Gotchas

- Size the output buffer with the matching \*_check function (the README says a safe NFKD/NFKC bound is about 11x the input). The NF(K)C check deliberately overestimates since an ASan-caught overrun fix (db3117a).
- The NEON loop does oversized stores by design ('It is possible that we do buffer overruns (but only _use_ the appropriate number of bytes)'), guarded by a 64-byte margin on input length. Leave slack after the output buffer rather than allocating exactly the normalized length.
- The README documents uint8_t\* parameters, but xxutf.h declares const char\* input and char\* output.
- Unicode 17.0.0 data is compiled in. To compare outputs with ICU, use an ICU built for the same Unicode version; a Unicode upgrade needs a rebuild that regenerates the tables.

## Known shortcomings

- Unicode normalization (NFD), moved to wave 3's unicode-utf8 category (ICU baseline). Public code (bin/benchmark/benchmark.zig plus bin/common/shim.c, Zig 0.16.0 ReleaseFast) but no CPU, ICU version or ICU flags, and no numeric table or result file: the chart was read by pixel (non-Latin 3.2x-4.5x, Latin 34.85 vs 0.34 GB/s, pure-ASCII pass-through). Output matches ICU's NFD (fuzzed against ICU4C), but ICU pays a UTF-8 to UTF-16 round trip in the harness. The chart predates the ASCII fast-path fix 5d54cc2.
- No x86 SIMD (NEON plus scalar only) and no MSVC build (GCC and Clang builtins). NEON paths do oversized stores by design, so the output buffer needs slack. Commit 5d54cc2 fixed a missing last_ccc reset in normalize and a missing \*out_length += 63 in the ASCII check path (0.2.0 shipped after it); an earlier ASan-caught NF(K)C size overrun was fixed in db3117a. The fuzzer covers valid UTF-8 up to 2048 bytes, NFD by default.

## Caveats and trade-offs

No numeric table or result file: values come from a PNG chart and are approximate (+/-0.05 GB/s per bar). CPU model, OS, ICU version and ICU build flags are not stated; the README only says 'a machine supporting ARM NEON' and asks users to match ICU's Unicode version to xxUTF's (Unicode 17.0.0). The chart was last regenerated in commit 4d1689f 'Improve ASCII normalization' (2026-06-26), and the next commit 5d54cc2 'Fix edge case bugs induced by previous commit' fixed the NEON UTF-8 ASCII fast path (missing '\*out_length += 63' and 'last_ccc = 0' resets), so the chart was measured on code later fixed for correctness bugs (the fix adds a few scalar operations per block and probably changes speed little). The Latin bar (about 100x) is pure-ASCII already-normalized text and reflects a pass-through, not decomposition work; per-chunk timing of 4 KiB at about 35 GB/s is roughly 110 ns per timed interval (derived), so timer resolution affects that bar. ICU is charged for UTF-8 to UTF-16 and back conversion around unorm2_normalize; ICU's C++ Normalizer2::normalizeUTF8 was not tried. Unpublished ICU case-fold and UTF-16 benchmark variants are biased against ICU (ucasemap_open/close or ucnv_open/close inside every timed chunk, and ucnv transcoding of UTF-16 input). The work is equivalent in output: NFD is standard-defined, xxUTF case folding uses full folding (CaseFolding.txt C and F entries, Turkic and simple skipped) like ICU's U_FOLD_CASE_DEFAULT, and the AFL++ fuzzer (test/fuzz.c) checks every output against ICU4C. Alpha status per README with a security review pending; 15 stars. Category: Unicode text processing (normalization and case folding), wave 3's unicode-utf8 category with an ICU baseline, not font shaping or layout.

C library distributed as a single-header amalgamation (callable from C++), no allocation, no libc dependency, UTF-8/UTF-16LE/UTF-16BE, NFD/NFC/NFKD/NFKC plus case folding, streaming helpers. Built for Unicode 17.0.0. README shows ARM NEON results and says not many instruction sets are supported yet (it claims to be fastest even in scalar mode). Build system is Zig 0.16.0. Input is assumed valid.

## Maintenance

Active alpha (v0.2.0, last commit 2026-07-11, MIT, 15 stars); small and dependency-free enough to vendor as one file, but treat it as pre-1.0 and validate input upstream.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-01): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README chart (doc/neon_utf8_nfd.png) of xxutf_utf8_nfd vs icu_utf8_nfd produced by public benchmark code (bin/benchmark/benchmark.zig, ICU calls in bin/common/shim.c, inputs in bin/common/inputs) with the Zig 0.16.0 ReleaseFast build stated in build.zig, but no CPU model, ICU version or ICU build flags, so not A. Values exist only as bar heights; no numeric table or result file is committed.
- **Verifier notes:** Record accurate: the eyeballed values match the chart within one pixel; pinned down with pixel measurements (no numeric table or result file exists). Benchmark code is real and like-for-like in output (fuzzed against ICU4C), with ICU paying UTF-16 transcoding; chart numbers predate a correctness fix to the ASCII fast path one commit later. Category for the orchestrator: Unicode text processing (wave 3 unicode-utf8, ICU baseline), not shaping; metadata verified (MIT, 15 stars, last commit 2026-07-11, active).
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `compiler_and_flags`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/dzfrias/xxUTF>
  - <https://github.com/dzfrias/xxUTF/commits/main>
  - <https://github.com/dzfrias/xxUTF/commits/main/doc/neon_utf8_nfd.png>
  - <https://github.com/dzfrias/xxUTF/commit/5d54cc2d143daf3ddcf85ec61abc693dde7fed5e>
  - <https://github.com/dzfrias/xxUTF/tree/main/doc>
  - <https://github.com/dzfrias/xxUTF/tree/main/bin/common/inputs>
  - <https://github.com/dzfrias/xxUTF/tree/main/.github/workflows>
  - <https://github.com/dzfrias/xxUTF/issues>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/README.md>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/build.zig>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/bin/benchmark/benchmark.zig>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/bin/common/shim.c>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/doc/neon_utf8_nfd.png>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/bin/common/inputs/Latin.txt>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/bin/common/inputs/Korean.txt>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/bin/common/inputs/Arabic.txt>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/gen/gen.py>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/test/README.md>
- **Sources the enricher read:**
  - <https://github.com/dzfrias/xxUTF>
  - <https://github.com/dzfrias/xxUTF/commits/main>
  - <https://github.com/dzfrias/xxUTF/tree/main/impl>
  - <https://github.com/dzfrias/xxUTF/tree/main/impl/neon>
  - <https://github.com/dzfrias/xxUTF/commit/db3117a>
  - <https://github.com/dzfrias/xxUTF/commit/5d54cc2d143daf3ddcf85ec61abc693dde7fed5e>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/README.md>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/build.zig>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/bin/benchmark/benchmark.zig>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/bin/common/shim.c>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/test/README.md>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/test/fuzz.c>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/impl/neon/neon_normalize_utf8.c>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/impl/neon/neon_common.h>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/xxutf.h>
  - <https://raw.githubusercontent.com/dzfrias/xxUTF/HEAD/common_defs.h>
  - <https://github.com/simdutf/simdutf/pulls?q=is%3Apr+author%3Adzfrias>
  - <https://github.com/simdutf/simdutf/pull/999>
- **Raw records:** [data/wave10/verified.json](../../../data/wave10/verified.json) (id `https://github.com/dzfrias/xxutf`) · [data/wave10/enrich/raw/github_com_dzfrias_xxutf.json](../../../data/wave10/enrich/raw/github_com_dzfrias_xxutf.json) (enrichment confidence 0.78)

</details>
