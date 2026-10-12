# mail-parser (Rust e-mail parser)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Other languages beating C, C++ and assembly](../README.md) › [Strings and text](README.md)</sub>

**Tier A** (reproducible public benchmark) · Copyable · `Rust` · `Apache-2.0 OR MIT` · 🟢 active

> Rust RFC 5322/MIME e-mail parser with SIMD scanning and lazy zero-copy decoding; 9x to 31x GMime, VMime, libEtPan!, Dovecot.

| | |
|---|---|
| **Beats** | GMime 3.2.15, VMime (commit 5b01911), libEtPan! 1.10.1 and Dovecot 2.4.5 lib-mail (all C or C++, built with -O3 and called through C/C++ shims); the Rust mailparse 0.17.0 crate is also measured |
| **Claimed result** | README, geometric mean over the corpora shown in the README tables (7 corpora for full, 6 for headers and structure), with range: full workload 31x GMime (13 to 177), 20x VMime (7.8 to 80), 15x libEtPan! (5.7 to 69), 9.3x Dovecot (4.4 to 24), 3.0x mailparse; headers 14x GMime, 33x VMime, 19x libEtPan!, 5.2x Dovecot; structure 14x GMime, 31x VMime, 17x libEtPan!, 3.9x Dovecot. Example, full workload, Enron 3,000 messages: mail-parser 2,420 MiB/s vs GMime 65, VMime 70, libEtPan! 96, Dovecot 366 MiB/s (results/summary.md: 37.10x, 34.77x, 25.23x, 6.60x). |
| **Workload** | Parse RFC 5322/MIME e-mail messages (one message per call) in three workloads: full (parse and read every decoded leaf body with charset conversion to UTF-8), headers (decoded Subject, first From address, Date, Message-ID) and structure (content type of every MIME part), over eleven corpora (3,292 messages, 17.8 MiB: test suite, Enron sample, large attachments, newsletters, long header blocks, forwarded messages, 1 MB plain text). |
| **Metric** | throughput |
| **Hardware** | Apple M4 Mac mini (4 performance and 6 efficiency cores, 16 GB), macOS 26.6.2, measured 2026-09-28; median over three runs of criterion's median (30 samples, 3 s measurement, 0.5 s warm-up), runs gated on a machine-wide idle lock. |
| **Compiler and flags** | Rust side: mail-parser 1.0.0 from the repository (the unreleased rewrite; crates.io latest is 0.11.9, which the harness also measures but the published tables leave out), feature full_encoding, rustc 1.98.1, release profile (opt-level 3, debug line-tables only; no LTO or PGO set), criterion 0.8.2. C/C++ side (benches/compare/README.md, vendor/build.sh OPT=-O3): Apple clang 21.0.0 (clang-2100.3.34.2); GMime 3.2.15 configure CFLAGS=-O3 --disable-crypto; VMime master 5b01911 CMake Release CMAKE_CXX_FLAGS_RELEASE='-O3 -DNDEBUG'; libEtPan! 1.10.1, 22 parser sources compiled at -O3; Dovecot 2.4.5 lib-mail/lib-charset/lib configure CFLAGS=-O3; shims compiled by build.rs at opt_level 3 (-std=gnu11, -std=c++17). GLib (Homebrew 2.90.0) and the macOS system iconv used for charset conversion are prebuilt system libraries, not built by the harness. |
| **Kind** | library or program |
| **Same algorithm as the baseline** | no |
| **Same optimization level** | yes |
| **Why it wins** | README feature list: SIMD kernels find boundaries and header fields (NEON on aarch64, AVX2 and SSE2 on x86-64), SIMD base64 and quoted-printable decoders (encodify), simdutf8 for UTF-8 validation, perfect hashing (hashify) for header names, charset labels and HTML entities, lazy decoding (bodies are not transfer-decoded or charset-converted until read) and zero-copy strings that borrow from the input. |
| **Adoption** | 462 stars, 64 forks; mail-parser crate 4,234,073 downloads on crates.io (latest release 0.11.9); parser inside Stalwart Mail Server |
| **Last commit** | 2026-10-10 |
| **Links** | [repository](https://github.com/stalwartlabs/mail-parser) · [benchmark](https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/README.md) |

## Verdict

On an Apple M4 Mac mini (macOS 26.6.2), mail-parser 1.0.0 built by rustc 1.98.1 (release, opt-level 3) was timed with criterion against GMime 3.2.15, VMime master 5b01911, libEtPan! 1.10.1 and Dovecot 2.4.5 lib-mail, all built from pinned sources at -O3 with Apple clang 21 and driven through project-written C/C++ shims, median of three runs over 11 corpora: full-workload geometric means of 31x GMime, 20x VMime, 15x libEtPan!, 9.3x Dovecot and 3.0x mailparse, headers 5.2x to 33x, with a published equivalence check showing equal message, part and leaf counts on Enron and the generated corpora.

## Use it when

- Rust mail servers, indexers, spam or DKIM pipelines that parse many messages but read few bodies: on the author's Apple M4 the headers workload runs 2,638 MiB/s on Enron (Dovecot 480, libEtPan! 266, VMime 137, GMime 132).
- Full decoding of ordinary mail: Enron full workload 2,420 MiB/s vs Dovecot 366, libEtPan! 96, VMime 70 and GMime 65; attachment-heavy messages 12.7 GB/s vs GMime 960 MiB/s.
- JMAP or IMAP servers that need RFC 8621 body lists, has_attachments(), part roles and decode-problem flags (isEncodingProblem) rather than raw MIME trees.
- Untrusted input: the parser has nesting, part-count and encoded-nesting limits (64, 10,000 and 3 by default), cargo-fuzz targets for parser, fields, charsets, kernels and mbox, and Miri test runs.

## Skip it when

- C or C++ code bases: Rust only, so you need your own FFI layer; the 1.0 line requires Rust 1.98, a very recent toolchain.
- You need a released, stable API today: the benchmarked 1.0.0 is an unreleased breaking rewrite; crates.io still serves 0.11.9 (2026-09-09), which decodes every body during parse, has a different API and is not in the published tables.
- Streaming or very large inputs: parse() takes the whole message as one slice and returns None for input of 4 GiB or more; Dovecot's istream-based message-parser works block by block.
- Building, editing or re-serialising messages: the parsed message is read-only (use mail-builder).
- Legacy CJK mail without the full_encoding feature: those bodies are decoded as UTF-8 and reported as an unknown charset.

## How it is fast

SIMD kernels (NEON on aarch64, AVX2 and SSE2 on x86-64, memchr elsewhere) find MIME boundaries and header-field ends; header names, charset labels and HTML entities are looked up with compile-time perfect hashing (the hashify crate); a message is stored in a handful of flat vectors and strings borrow from the input (zero-copy). Nothing is decoded during parse; when a body is read, Base64 and quoted-printable go through encodify's SIMD codecs and UTF-8 is validated with simdutf8. parse_with() plus MessageBuffers reuses one message's storage for the next.

## Compared with alternatives

No other e-mail parser is catalogued; encodify (its Base64/quoted-printable layer) is the sibling to take when you only need transfer encodings without MIME parsing. Against the most used Rust parser, mailparse 0.17.0 (not catalogued), mail-parser is 1.3x to 4.6x faster on the full workload of the README corpora (3.0x geometric mean; 1.25x on the 1 MB plain-text body) and also handles boundary-prefix lines correctly where mailparse splits them.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | hashify 0.3, memchr 2.8, simdutf8 0.1, encodify 1.0; optional encoding_rs 0.8 (full_encoding) and serde |
| **Minimum toolchain** | Rust 1.98 for 1.0.0 (repository; edition 2024); 0.11.9 on crates.io has no declared MSRV |
| **Platforms** | any Rust target; SIMD kernels on aarch64 (NEON) and x86-64 (AVX2 and SSE2), memchr fallback elsewhere; only Apple silicon macOS was benchmarked |
| **Thread safety** | MessageParser, Message and the views are Send + Sync (README and CHANGELOG); build one parser and share it; parse_owned() gives a Message&lt;'static&gt; that can move between threads |
| **Drop-in for the baseline** | no |

## Gotchas

- Harness asymmetry in the full workload: the GMime shim calls g_mime_text_part_get_text, which in GMime 3.2.15 opens an iconv filter whenever a charset parameter is present, UTF-8 to UTF-8 included (gmime-text-part.c lines 280-288, no same-charset shortcut in g_mime_filter_charset_new), while the VMime and libEtPan! shims skip conversion for UTF-8 bodies and only run g_utf8_validate_len. So GMime's 1 MB UTF-8 body goes through macOS iconv at 97 MiB/s against 2,212 (VMime) and 2,796 (libEtPan!), which is the 176.61x top of the README's '13 to 177' range; without that corpus the GMime full geometric mean is about 23x rather than 31x (derived from page data in results/summary.md). It is GMime's ordinary API, but the shims are not tuned equally.
- The headers and structure ratios measure header parsing plus boundary scanning only: no library decodes bodies there, throughput is corpus bytes over time, so corpora with large bodies reach 80,868 MiB/s and the 1 MB plain-text cells hundreds of GB/s; the README excludes plain-large from those geometric means but not from the full one.
- The numbers were measured on 2026-09-28 at the 1.0.0 merge; later commits (SSSE3 tier, charset label remapping, an address-lexer fix for backslash escapes #162, HTML text fixes) were not re-measured. Only one machine was used (Apple M4, NEON path); the AVX2/SSE2 kernels, Linux, glibc iconv and distribution GLib were not measured, and GMime and VMime copy the input into their own streams as their users would.
- unsafe is confined to the SIMD kernels and a UTF-8 module that turns already-validated bytes into str/String; Miri cannot run every NEON instruction encodify uses, so the parser's Miri runs use encodify's portable path (--cfg encodify_scalar, which only works from encodify 1.0.1).

## Known shortcomings

- First-party shims; lazy decoding inflates the headers and structure ratios; the C side uses system iconv and GLib; Apple M4 only; the measured version is the unreleased repo 1.0.0 (crates.io latest 0.11.9); an equivalence check (check.md) exists.
- Harness flaw: the GMime shim calls g_mime_text_part_get_text, which in GMime 3.2.15 always runs iconv when a charset is set, UTF-8 to UTF-8 included (gmime-text-part.c 280-288), while the VMime and libEtPan! shims skip UTF-8 conversion; GMime therefore reaches only 97 MiB/s on the 1 MB UTF-8 body, the 176.61x top of the README range, and without that corpus the GMime full geomean is about 23x, not 31x (derived). 1.0.0 is unreleased, MSRV 1.98, Apple M4 only, measured before later edge-case fixes (#162, charset labels).

## Caveats and trade-offs

The measured mail-parser is 1.0.0 from the repository, an unreleased rewrite; the latest crates.io release (0.11.9) decodes every body during parse and is not in the published tables. First-party harness, but results/check.md shows equal message, part and leaf counts on Enron and the generated corpora and decoded bytes within 2% on the test suites (Dovecot -6%); mailparse and Dovecot dashes-crlf cells do work that is not comparable (excluded from README tables); GMime finds no From mailbox in 327 Enron messages. Wins include lazy decoding: headers and structure never decode bodies, so large-attachment corpora reach 80,868 MiB/s. C/C++ libraries are driven through project-written shims, built without crypto, SSL and other optional features; charset conversion goes through macOS's system iconv and the C shims validate UTF-8 with GLib's g_utf8_validate_len, while mail-parser uses its own decoders and simdutf8, so part of the full-workload gap is library choice outside the parser. GMime, VMime and libEtPan! copy the input or bodies as their users would. One machine (Apple M4, NEON path); the AVX2/SSE2 x86-64 path is not measured. The nearest competitor is the Rust mailparse crate, 2.8x to 3.2x behind. Wins come from SIMD kernels, perfect hashing, lazy and zero-copy design, not from the language alone. [retier] The GMime shim calls g_mime_text_part_get_text, which in GMime 3.2.15 always runs iconv when a charset is set, UTF-8 to UTF-8 included, while the VMime and libEtPan! shims skip UTF-8 conversion; GMime therefore reaches only 97 MiB/s on the 1 MB UTF-8 body (the 176.61x top of the range), and without that corpus the GMime full geomean is about 23x, not 31x. 1.0.0 is unreleased, MSRV 1.98, Apple M4 only, measured before later edge-case fixes (#162).

Rust API; C++ callers need FFI. Bodies are decoded lazily, so the headers and structure workloads skip body work. Legacy CJK multi-byte charsets need the optional encoding_rs dependency. Does not build messages (separate mail-builder crate).

## Maintenance

Actively maintained (last commit 2026-10-10, about 4.25 million crates.io downloads, the parser of Stalwart Mail Server, Apache-2.0 OR MIT, copyable), but the measured 1.0.0 rewrite is unreleased and needs Rust 1.98; tier A harness whose GMime column pays a UTF-8-to-UTF-8 iconv pass the other C shims skip.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): confirm; tier before verification A, tier now A.
- **Tier reason:** Public harness benches/compare (vendor/build.sh builds GMime, VMime, libEtPan! and Dovecot lib-mail from SHA-256-pinned sources at -O3; build.rs compiles the shims at opt_level 3; criterion bench benches/compare.rs) with compiler versions (rustc 1.98.1, Apple clang 21.0.0), flags and CPU (Apple M4) stated in README and results/summary.md, plus a published equivalence check (results/check.md); every README number matches summary.md.
- **Verifier notes:** Confirm A; numbers match README and results/summary.md, harness flags and compiler versions are stated, equivalence check exists. Correct the measured version (repository 1.0.0, unreleased, not 0.11.9). Shortcomings: first-party shims, lazy decoding inflates headers/structure ratios, system iconv/GLib on the C side, Apple M4 only.
- **Fields the verifier corrected:** `compiler_and_flags`, `hardware`, `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-103 (wave 14); enricher (wave 14 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/README.md>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/README.md>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/results/summary.md>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/results/check.md>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/build.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/vendor/build.sh>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/Cargo.toml>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/Cargo.toml>
  - <https://github.com/stalwartlabs/mail-parser>
  - <https://github.com/stalwartlabs/mail-parser/commits/main>
  - <https://crates.io/api/v1/crates/mail-parser>
- **Sources the enricher read:**
  - <https://github.com/stalwartlabs/mail-parser/issues>
  - <https://github.com/stalwartlabs/mail-parser/commits/main>
  - <https://github.com/stalwartlabs/mail-parser/commit/79b2f3f>
  - <https://github.com/stalwartlabs/mail-parser/commit/4a6bacf>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/README.md>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/Cargo.toml>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/README.md>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/results/summary.md>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/results/check.md>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/build.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/vendor/build.sh>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/Cargo.toml>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/benches/compare.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/src/impls/mod.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/src/impls/v1.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/src/impls/mailparse.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/src/ffi.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/src/workload.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/src/tally.rs>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/shim/gmime.c>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/shim/vmime.cpp>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/shim/libetpan.c>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/shim/dovecot.c>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/shim/utf8.c>
  - <https://raw.githubusercontent.com/stalwartlabs/mail-parser/HEAD/benches/compare/shim/tally.h>
  - <https://raw.githubusercontent.com/jstedfast/gmime/3.2.15/gmime/gmime-text-part.c>
  - <https://raw.githubusercontent.com/jstedfast/gmime/3.2.15/gmime/gmime-filter-charset.c>
  - <https://raw.githubusercontent.com/jstedfast/gmime/3.2.15/gmime/gmime-iconv.c>
  - <https://raw.githubusercontent.com/stalwartlabs/hashify/HEAD/README.md>
  - <https://crates.io/api/v1/crates/mail-parser>
  - <https://crates.io/api/v1/crates/mail-parser/reverse_dependencies>
- **Raw records:** [data/wave14/verified.json](../../../data/wave14/verified.json) (id `https://github.com/stalwartlabs/mail-parser`) · [data/wave14/enrich/raw/github_com_stalwartlabs_mail_parser.json](../../../data/wave14/enrich/raw/github_com_stalwartlabs_mail_parser.json) (enrichment confidence 0.8)

</details>
