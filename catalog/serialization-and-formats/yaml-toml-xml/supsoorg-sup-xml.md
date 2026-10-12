# SupXML (sup-xml)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Serialization and formats](../README.md) › [YAML, TOML and XML](README.md)</sub>

**Tier C** (first-party claim) · Study only · `Rust` · `Proprietary source-available (Supported Source; LICENSE requires a paid or free-tier license certificate to use the code; not OSI)` · 🟢 active

> Source-available Rust XML stack with a libxml2-compatible C ABI; the vendor reports \~2.1x median DOM-parse throughput over libxml2.

| | |
|---|---|
| **Beats** | libxml2 |
| **Claimed result** | DOM parse vs libxml2 xmlParseMemory: \~2.1x median across 21 fixtures, faster on every fixture shown (e.g. gazali_maqasid_ar 599 KB 539 vs 144 MB/s = 3.75x; wikipedia_ww2 252 KB 1170 vs 395 MB/s = 2.96x; swiss_prot 95 MB 177 vs 94 MB/s = 1.88x); W3C XSTS 1.0 wall-clock: schema compile 1.74 s vs 3.96 s (\~2.3x), instance validate 1.12 s vs 2.85 s (prose calls this 'parity'), total 2.86 s vs 6.81 s (\~2.4x end-to-end, libxml2's 3 timed-out cases excluded); HTML5 parse \~1.02x geomean vs libxml2 (parity) |
| **Workload** | DOM parsing of 21 checked-in XML fixtures (11 shown on the page, 15 KB-95 MB) into an owned tree under a 'matched contract' harness (cargo bench -p sup-xml-bench --bench head_to_head); plus W3C XSD 1.0 test suite (XSTS 2006-11-06, 14,328 schemaTests, 25,092 instanceTests) conformance and wall-clock (xsts_compliance bench) |
| **Metric** | throughput |
| **Adoption** | 1 star; 121 crates.io downloads (sup-xml 1.3.0) |
| **Last commit** | 2026-06-20 |
| **Links** | [repository](https://github.com/SupsoOrg/sup-xml) · [benchmark](https://supso.org/projects/sup-xml/docs/reference/performance/) |

## Verdict

This is a first-party bench (cargo bench -p sup-xml-bench --bench head_to_head). It compares sup-xml's bumpalo-arena DOM (parse_bytes_unchecked, default options, input copied into an owned buffer) with libxml2 xmlParseMemory plus xmlFreeDoc through FFI, taking best-of-N MiB/s per fixture. The 11 fixtures shown range from 1.61x to 3.75x, the claimed median over 21 is \~2.1x, and the XSTS 1.0 wall-clock is 2.86 s vs 6.81 s with libxml2's 3 timeouts excluded. No CPU, OS, rustc version, flags or libxml2 version is disclosed; build.rs links whatever libxml2 pkg-config or the macOS system provides, and the numbers have not been independently reproduced.

## Use it when

- Rust services that need libxml2-class features (XSD 1.0 validation, XPath 1.0, XSLT, C14N for XML-DSig/SAML, recovery mode) without linking C, and that can get a Supso certificate: paid commercial, free 30-day evaluation, or free hobbyist for non-monetized projects
- DOM-parsing UTF-8 documents from about 15 KB to 95 MB into an owned tree. The vendor's table shows 1.61x (pubmed) to 3.75x (Arabic gazali_maqasid_ar, 599 KB) over libxml2's xmlParseMemory; the largest gains are on text-heavy and non-ASCII documents
- XSD pipelines with complex Microsoft-style particle and derivation schemas. On W3C XSTS 1.0, libxml2 goes quadratic and times out at 30 s on 3 schemas that SupXML compiles in under 1 ms, and total schema-compile time is 1.74 s vs 3.96 s
- Browser or edge runtimes that need XML, XPath, XSLT, XSD or HTML parsing: it builds for wasm32-unknown-unknown with every feature except network-resolver
- As a reference design for a strict, validating XML tokenizer built from memchr, SWAR and lookup tables

## Skip it when

- Any open-source, redistributable or unlicensed deployment. The LICENSE is proprietary Supported Source (not OSI), and every document-parse entry point returns a fatal error unless a valid certificate is found
- Pure streaming or event workloads. The vendor's own page shows quick-xml faster on 4 of the 5 fixtures it lists (nasa 0.74x, swiss_prot 0.59x, wikipedia_ww2 0.11x), with only \~1.04x median across 21 fixtures at the matched contract
- Maximum DOM speed on trusted input. Its own docs say parse_bytes_in_place with all four skip_\* flags reaches 'roughly half of pugixml's throughput', and pugixml-beating siblings go further
- HTML parsing for speed. It wraps html5ever and is at parity with libxml2 (\~1.02x geomean on the docs page); COMPARISON.md even shows hn.html at 35 vs 45 MiB/s
- Long-running processes that use the C-ABI shim on persistent threads, because per-document arenas are freed only at thread exit. Also note the maturity: 1 contributor, 1 GitHub star and 121 crates.io downloads

## How it is fast

The tokenizer is a strict byte-level SAX reader built on memchr SIMD searches. Text runs scan for '&lt;', '&' and ']' in one memchr3 pass. A start tag jumps to the first '&gt;' and accepts it if a memchr2 count of both quote characters before it is even; otherwise it falls back to a quote-aware scan. XML Name characters are checked against 256-entry ASCII lookup tables. XML 1.0 §2.2 character validation is one upfront SWAR pass over the whole document (the has-zero-byte trick, 8 bytes per iteration) instead of per-token checks, and UTF-8 is validated with simdutf8 (AVX2/SSE4.2/NEON dispatch). The DOM uses libxml2-shaped nodes allocated in one bumpalo arena per document, so each node costs a pointer bump and the whole arena is freed at once. Strings are borrowed from the owned source buffer where possible. An opt-in parse_bytes_in_place mode decodes entities inside the input buffer to avoid copies.

## Compared with alternatives

Choose it over yxml, quick-xml, xmloxide or rusty_xml only when you need libxml2's broader surface (XSD, XSLT, XPath, C14N, recovery) in memory-safe Rust or behind a libxml2 C ABI, and you are willing to license it. For plain streaming, quick-xml beats it on most fixtures in SupXML's own table. yxml offers a similar \~2.2-2.4x over libxml2 in a tiny C SAX parser. xmloxide is the other pure-Rust libxml2 reimplementation, catalogued at roughly libxml2 parity.

## Integration

| | |
|---|---|
| **Form** | crate (sup-xml on crates.io); C callers use a cdylib (libsupxml2.so/.dylib) built from the unpublished crates/compat with --features cdylib-exports |
| **Dependencies** | supso-project (offline Ed25519 + ML-DSA-44 license verification), memchr, simdutf8, bumpalo, rustc-hash, regex, chrono, rust_decimal, elsa, unicode-properties, log, encoding_rs (default full-encodings feature); optional: html5ever/markup5ever (html), ureq (network-resolver), bitflags (xsd) |
| **Minimum toolchain** | Rust 1.85 (edition 2024) |
| **Platforms** | any Rust target; SIMD UTF-8 validation dispatches at runtime (AVX2/SSE4.2/NEON) with a scalar fallback; wasm32-unknown-unknown supported except the network-resolver feature |
| **Thread safety** | Document is Send but not Sync. Parsing shares no mutable state, so any number of threads can parse concurrently. In the C shim each document gets its own arena, and the arena is kept alive until the thread exits. |
| **Drop-in for the baseline** | partial — the Rust API is not libxml2's. The compat cdylib exports libxml2 symbol names and struct layouts, and the vendor reports lxml 47/47 and Nokogiri 17/17 operations identical after rebuilding those bindings against a system libxml2. Differences: Perl XML::LibXML's xmlTextReader usage is not yet covered, the entity-expansion cap is 1 MB vs libxml2's \~10 MB, recovery keeps a bare '&' where libxml2 drops the text, and node memory is freed only at thread exit. cdylib-exports is off by default because linking the shim and the real libxml2 into one binary causes undefined behavior (xmlFree shadowing). |

## Gotchas

- Runtime license gate: the first parse in a process looks for a certificate (SUPSO_LICENSE_PATH, \~/.supso/license_certificates/, ./.supso/license_certificates/). Without one, every parse returns a fatal error. An expired certificate only gets a logged grace period before parsing fails.
- The headline benchmark is not symmetric. The timed sup-xml call is parse_bytes_unchecked, which skips encoding sniffing and SIMD UTF-8 validation (the harness checks UTF-8 outside the timer). It also runs with the default namespace_aware: false, so there is no xmlns scanning or QName resolution. libxml2's xmlParseMemory does detection and validation inside the timer and uses its namespace-aware SAX2 interface. Timing is best-of-N with no warmup (default N=2), and 'MB/s' is actually MiB/s.
- The project's own documents disagree. COMPARISON.md gives \~1.0-1.3x median vs libxml2 against the docs page's \~2.1x. The README claims 255/257 on the W3C XML Conformance Suite, but the COMPARISON.md table shows 244/257. An XSD instance-validate time of 1.12 s vs 2.85 s is described as 'parity'. A bench comment still says gazali parses at \~14 MB/s vs libxml2's \~140 MB/s.
- The defaults differ from libxml2: namespace_aware is false (set it true for prefixed XPath), there is a 1 MB entity-expansion cap and a depth limit of 256, and external DTDs are not loaded. The 'memory-safe' claim is scoped: unsafe code is allowed in the scanner, readers, parser, encoding and dom.rs, and the C shim is #![allow(unsafe_code)] even though CONTRIBUTING lists the shim among the forbid-unsafe modules.

## Known shortcomings

- Proprietary source-available licence (needs a licence certificate). The timed SupXML run skips UTF-8 validation (parse_bytes_unchecked) while libxml2 validates inside its timing, contradicting the page's 'matched contract' claim. No CPU, rustc or libxml2 version; the repo's own COMPARISON.md says only \~1.0-1.3x vs libxml2; the XSD validation text and table disagree. 1 star.
- The timed run also skips encoding sniffing and namespace processing (namespace_aware false) while libxml2 is namespace-aware; best-of-2, no warmup. The project's documents contradict each other (COMPARISON.md \~1.0-1.3x vs the docs page's \~2.1x; W3C suite 255/257 vs 244/257). By its own numbers quick-xml streams faster on 4 of 5 fixtures and its fastest DOM mode reaches about half of pugixml. The libxml2 C shim frees arenas only at thread exit and is off by default because linking it with real libxml2 is undefined behaviour. Parsing hard-fails without a licence certificate. Enrichment confidence 0.4.

## Caveats and trade-offs

No CPU model, rustc version, build flags or libxml2 version disclosed. In head_to_head.rs the timed sup-xml path calls parse_bytes_unchecked, which 'skips the upfront UTF-8 validation' (the harness checks UTF-8 outside the timed region), while libxml2's xmlParseMemory validates inside the timing, which contradicts the page's claim that both sides validate UTF-8. Timing is best-of-N with no warmup (default N=2). The repo's own COMPARISON.md Performance table still says sup-xml vs libxml2 (default) is only \~1.0-1.3x median, which conflicts with the docs page's \~2.1x. The XSD totals exclude libxml2's 3 timed-out schemas, and the page contradicts itself: its table gives instance validate as 1.12 s vs 2.85 s (\~2.5x), but the prose says 'parity on validate'. Proprietary license (certificate required, and parsing fails without one), so it is reference only. No independent reproduction found.

GitHub reports the license as 'Other'/NOASSERTION rather than a recognized OSI license, so the code can be studied but not safely reused despite being public; single-maintainer org with essentially no adoption; ships a drop-in C ABI for libxml2 callers but is a from-scratch Rust reimplementation

## Maintenance

The project is actively developed by a single maintainer (111 commits from one contributor; v1.3.0 released 2026-06-17; last commit 2026-06-20). It is reference-only here because the proprietary Supported Source license requires a paid or free-tier certificate, and parsing fails without one.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The performance page shows a DOM-parse table against libxml2 (xmlParseMemory) and XSD wall-clock numbers. The benchmark code is public (crates/bench/benches/head_to_head.rs, xsts_compliance.rs), but no CPU, rustc version, flags or libxml2 version is stated anywhere (page, README, COMPARISON.md), so it cannot be A. It is first-party, so C.
- **Verifier notes:** All headline numbers are on the docs page. The record's fixture range '7.9KB-95MB' was a misread: chinese1 is 7.9 MB and the smallest fixture shown is 15 KB. The XSD claim is clarified: compile \~2.3x, validate parity, end-to-end \~2.4x. The license is not null: LICENSE is a proprietary Supported Source certificate license (gh reports NOASSERTION). The UTF-8-unchecked timed path is worth flagging during enrichment.
- **Fields the verifier corrected:** `license`, `stars_or_usage`, `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://supso.org/projects/sup-xml/docs/reference/performance/>
  - <https://github.com/SupsoOrg/sup-xml>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/LICENSE>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/README.md>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/COMPARISON.md>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/bench/benches/head_to_head.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/core/src/parser.rs>
  - <https://crates.io/api/v1/crates/sup-xml>
- **Sources the enricher read:**
  - <https://github.com/SupsoOrg/sup-xml>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/README.md>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/COMPARISON.md>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/LICENSE>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/CONTRIBUTING.md>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/Cargo.toml>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/.cargo/config.toml>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/core/Cargo.toml>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/bench/Cargo.toml>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/bench/build.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/bench/benches/head_to_head.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/core/src/license_gate.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/core/src/parser.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/core/src/scanner.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/core/src/xml_bytes_reader.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/core/src/options.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/core/src/charsets.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/tree/src/dom.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/tree/src/dict.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/api/src/lib.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/compat/Cargo.toml>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/compat/src/lib.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/compat/src/dict.rs>
  - <https://github.com/SupsoOrg/sup-xml/blob/main/crates/compat/src/tree.rs>
  - <https://github.com/SupsoOrg/sup-xml/issues/1>
  - <https://github.com/SupsoOrg/sup-xml/releases>
  - <https://github.com/SupsoOrg/sup-xml/commits/main>
  - <https://github.com/SupsoOrg/sup-xml/graphs/contributors>
  - <https://supso.org/projects/sup-xml/docs/reference/performance/>
  - <https://supso.org/projects/sup-xml/docs/guides/migrating-from-libxml2/>
  - <https://crates.io/api/v1/crates/sup-xml>
  - <https://github.com/GNOME/libxml2/blob/master/include/libxml/parser.h>
- **Raw records:** [data/wave4/verified.json](../../../data/wave4/verified.json) (id `https://github.com/supsoorg/sup-xml`) · [data/wave4/enrich/raw/github_com_supsoorg_sup_xml.json](../../../data/wave4/enrich/raw/github_com_supsoorg_sup_xml.json) (enrichment confidence 0.4)

</details>
