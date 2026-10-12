# unicode-transforms

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Haskell` · `BSD-3-Clause` · 🟢 active

> Pure-Haskell Unicode NFC/NFKC/NFD/NFKD normalization for Text, beating ICU's C library binding on decomposition forms.

| | |
|---|---|
| **Beats** | ICU (ICU4C 65.1, via the text-icu Haskell binding) |
| **Claimed result** | Up to +376.87% (NFKD/Korean: 7.78 ms vs ICU 37.10 ms, \~4.8x). Wins all 14 NFD/NFKD rows (+8.82% to +376.87%) but only 5 of 14 NFC/NFKC rows; ICU is faster in 9 of 28 rows, e.g. NFC/Japanese -292.04% (11.90 vs 3.04 ms), NFC/AllChars -171.63%, NFC/Deutsch -54.39%, NFC/English -7.21%. |
| **Workload** | Unicode NFC/NFKC/NFD/NFKD normalization of per-language text files (Korean, Vietnamese, Deutsch, English, Devanagari, Japanese, AllChars), milliseconds per file |
| **Metric** | latency |
| **Hardware** | macOS (exact CPU model not stated) |
| **Adoption** | 48 stars |
| **Last commit** | 2026-01-18 |
| **Links** | [repository](https://github.com/composewell/unicode-transforms) · [benchmark](https://github.com/composewell/unicode-transforms#performance) |

## Verdict

The README's per-file wall-clock ms table (package v0.3.7) compares unicode-transforms against text-icu 0.x calling ICU4C 65.1, across 7 language corpora, on unstated macOS hardware (no CPU model, GHC version, or compiler flags given). unicode-transforms wins all 14 NFD/NFKD rows (+8.8% to +376.9%, e.g. NFKD/Korean 7.78ms vs ICU's 37.10ms) but loses 9 of 14 NFC/NFKC rows, including NFC/Japanese (11.90ms vs ICU's 3.04ms) and NFC/AllChars (9.72ms vs 3.58ms).

## Use it when

- Pure-Haskell codebases that want to drop the native ICU4C runtime dependency and FFI overhead of text-icu
- Decomposition-heavy workloads (NFD/NFKD): wins all 14 measured README rows, from +8.8% to +377% over ICU
- Batch/offline normalization of in-memory Data.Text values, e.g. Korean or Vietnamese text (largest measured wins)
- Projects on GHC 8.0.2 through 9.14.1 wanting a small dependency footprint (base, text, bytestring, ghc-prim, unicode-data only)
- Cases where a small, auditable pure-Haskell implementation is preferred over linking libicu

## Skip it when

- Composition-heavy workloads (NFC/NFKC): ICU is faster in 9 of 14 measured rows, e.g. NFC/Japanese 11.90ms vs ICU's 3.04ms, NFC/AllChars 9.72ms vs 3.58ms
- NFKC on Korean input specifically: open issue #106 reports NFKC is not idempotent on some Korean inputs — a correctness bug, not just a perf gap
- Need ICU features beyond normalization (collation, FCD normalization, string iteration, regex) — this package does normalization only
- Callers outside Haskell (C/C++/other languages) — there is no exposed FFI surface, it's a Haskell library only
- Need normalization numbers you can trust on your own hardware: the published table is for package v0.3.7 (current is 0.4.0.1), unspecified 'macOS' hardware with no CPU model, GHC version, compiler flags, or run date given

## How it is fast

It rides text's internal stream-fusion machinery (Data.Text.Internal.Fusion) to decompose/recompose characters while writing directly into a mutable Text array, avoiding intermediate list or Text allocations. Combining marks awaiting reorder by combining class are held in a small hand-unrolled buffer (`ReBuf = Empty | One Char | Many Char Char [Char]`) rather than a general list, so the common 0-2 mark case avoids list overhead. Hangul syllable decomposition/composition is done algorithmically instead of via UCD table lookup. The library is built with `-O2 -funbox-strict-fields -fspec-constr-count=10` (optional LLVM backend via a cabal flag).

## Compared with alternatives

The catalogued siblings are C/C++/Rust/Go SIMD UTF-8 validators/decoders, not Unicode normalizers, except Boost.Text (C++, also claims to beat ICU on NFC). Pick unicode-transforms over ICU (or Boost.Text) specifically when you're in a pure-Haskell codebase doing decomposition (NFD/NFKD) and want to remove the ICU4C runtime dependency; for NFC/NFKC-heavy or non-Haskell workloads, ICU or Boost.Text is likely still faster.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | base (&gt;=4.8,&lt;4.23), text (&gt;=1.1.1,&lt;=1.2.5.0 or &gt;=2.0,&lt;2.2), bytestring, ghc-prim, unicode-data |
| **Minimum toolchain** | GHC 8.0.2+ (CI tests through GHC 9.14.1); cabal-version 2.2 |
| **Platforms** | any (pure Haskell); CI covers Linux, Windows (AppVeyor), and s390x |
| **Thread safety** | not documented (pure, allocation-based functions; no stated concurrency caveats) |
| **Drop-in for the baseline** | partial — explain: same underlying Data.Text type and no native ICU dependency, but the API (Data.Text.Normalize.normalize) differs from text-icu's interface, so call sites must be rewritten |

## Gotchas

- Open bug: NFKC is not idempotent on some Korean inputs (issue #106, still open as of 2026-08-17)
- Ships a deprecated Data.ByteString.UTF8.Normalize module alongside the current Data.Text.Normalize API
- For some scripts (Japanese, AllChars) composition forms are markedly slower than ICU, up to roughly 4x, not just a modest loss
- Package is still marked 'Experimental' stability in its cabal file despite a decade of releases

## Caveats and trade-offs

No CPU model, GHC version, or compiler flags are stated (only 'macOS'), so capped at Tier C. Results are mixed: unicode-transforms wins every decomposition (NFD/NFKD) row, but ICU is faster in 9 of 14 composition (NFC/NFKC) rows, including NFC for English, Deutsch, Korean, Japanese and AllChars. ICU is called through the text-icu Haskell binding. The table is for v0.3.7 (current package version is 0.4.0.1), with no run date.

Haskell-only API (Data.Text.Normalize), not usable from C/C++ directly; performance varies heavily by script and normalization form.

## Maintenance

Actively maintained — last master commit 2026-01-18, adding support for newer GHC releases up through 9.14; BSD-3-Clause and small enough to vendor, but stability is marked 'Experimental' and there is an open correctness bug in NFKC on Korean text (issue #106).

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** README has a first-party per-file ms table against ICU4C 65.1 via text-icu, and benchmark code is public (benchmark/Benchmark.hs, benchmark/NormalizeFile.hs). Only 'macOS' is stated, with no CPU model, GHC version or flags, so C.
- **Verifier notes:** Table numbers verified verbatim in README. last_commit corrected: the newest default-branch (master) commit is 2026-01-18; the 2026-09-21 date is the repo pushed_at, likely from another branch. Still active; BSD-3-Clause and 48 stars confirmed.
- **Fields the verifier corrected:** `claimed_speedup`, `last_commit`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/composewell/unicode-transforms>
  - <https://github.com/composewell/unicode-transforms#performance>
  - <https://github.com/composewell/unicode-transforms/tree/master/benchmark>
  - <https://github.com/composewell/unicode-transforms/blob/master/unicode-transforms.cabal>
- **Sources the enricher read:**
  - <https://github.com/composewell/unicode-transforms>
  - <https://github.com/composewell/unicode-transforms#performance>
  - <https://github.com/composewell/unicode-transforms/blob/master/unicode-transforms.cabal>
  - <https://github.com/composewell/unicode-transforms/tree/master>
  - <https://github.com/composewell/unicode-transforms/blob/master/Data/Text/Normalize.hs>
  - <https://github.com/composewell/unicode-transforms/blob/master/NOTES.md>
  - <https://github.com/composewell/unicode-transforms/blob/master/Data/Unicode/Internal/NormalizeStream.hs>
  - <https://github.com/composewell/unicode-transforms/blob/master/Changelog.md>
  - <https://github.com/composewell/unicode-transforms/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/composewell/unicode-transforms`) · [data/wave3/enrich/raw/github_com_composewell_unicode_transforms.json](../../../data/wave3/enrich/raw/github_com_composewell_unicode_transforms.json) (enrichment confidence 0.6)

</details>
