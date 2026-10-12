# libidn

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `C` · `LGPL-3.0-or-later OR GPL-2.0-or-later` · 🟢 active

> GNU C library for IDNA2003, Stringprep and Punycode. One Ruby benchmark shows it \~1.47x faster than libidn2.

| | |
|---|---|
| **Beats** | libidn2 |
| **Claimed result** | Ruby Benchmark.bmbm output in benchmark/idna.rb, 100,000 to_ascii+to_unicode round trips of one domain. Rehearsal real time: pure Ruby 5.915326 s, libidn 0.522676 s, libidn2 0.763983 s. Measured pass real time: pure Ruby 6.043252 s, libidn 0.521704 s, libidn2 0.764863 s. libidn about 1.47x faster than libidn2 and about 11.6x faster than pure Ruby on the measured pass (derived from page data; 1.46x and 11.3x on the rehearsal). The PR author calls libidn2 'slightly slower than libidn1 as it's doing more work but nothing to worry about, we're still above 100k iterations/sec'. |
| **Workload** | Ruby benchmark/idna.rb in a pull request to the addressable gem: 100,000 cycles of converting the single domain string 'fiᆵリ宠퐱卄.com' to ASCII ('xn--fi-w1k207vk59a3qk9w9r.com') and back, through the pure Ruby IDNA code, the libidn (v1) backend and a new libidn2 FFI backend. |
| **Metric** | throughput |
| **Adoption** | 3 stars and 2 forks on the GitLab mirror (GitLab API); GNU library packaged by Linux distributions, though the GNU project now steers new users to libidn2 |
| **Last commit** | 2026-08-27 |
| **Links** | [repository](https://gitlab.com/libidn/libidn) · [benchmark](https://github.com/sporkmonger/addressable/pull/496) |

## Verdict

In an unmerged third-party Ruby PR (addressable #496), 100,000 to_ascii+to_unicode round trips of one domain string took 0.52 s with libidn (idn-ruby C extension), 0.76 s with libidn2 (Ruby FFI) and 6.04 s with pure Ruby: about 1.47x for libidn over libidn2. Hardware, OS, Ruby version and compiler are not stated, and the bindings and validation work differ between the two libraries.

## Use it when

- You must reproduce historic IDNA2003 output bit for bit, e.g. matching stored legacy names where 'faß.de' became 'fass.de'.
- You need a Stringprep profile (SASLprep, XMPP nodeprep/resourceprep, iSCSI, Kerberos V5) rather than domain-name processing. The README calls this and IDNA2003 compatibility the only reasonable uses today.
- C code on Unix or Windows that needs a small, stateless, re-entrant library with no required runtime dependencies on glibc systems.

## Skip it when

- Any new code that resolves, registers or compares domain names: IDNA2003 is superseded by IDNA2008, and its maintainers ask users to migrate to libidn2. Outputs differ, e.g. 'faß.de' gives 'fass.de' here but 'xn--fa-hia.de' under libidn2 non-transitional, so you can end up at a different host.
- As a speed upgrade over libidn2: the only number is one Ruby benchmark (one domain string, 5.2 vs 7.6 us per round trip) through unequal bindings. No C-level measurement exists.
- Text containing characters assigned after Unicode 3.2: the IDNA2003 tables stop there, so newer code points are rejected unless IDNA_ALLOW_UNASSIGNED is set, and then they pass unchecked.
- Projects that cannot accept LGPL-3.0-or-later / GPL-2.0-or-later terms (the idn tool is GPL-3.0-or-later). libidn2 carries the same terms, so switching libraries does not help.

## How it is fast

ToASCII runs the Nameprep profile, then RFC 3492 Punycode encoding. Nameprep does character mapping and prohibited/bidi checks by bsearch over RFC 3454 range tables, plus NFKC normalization through code taken from GLib. A source comment says this table lookup once took nearly all CPU time; switching from a linear scan to bsearch cut fuzz-corpus time about 20x, and _g_utf8_normalize_wc now dominates. Its edge over libidn2 comes mostly from doing less per label: no UTS #46 mapping pass, no NFC re-check, no IDNA2008 CONTEXTJ/CONTEXTO or unassigned-code-point tests when IDNA_ALLOW_UNASSIGNED is passed, and no punycode round-trip in ToASCII.

## Compared with alternatives

Pick it only when IDNA2003 or Stringprep semantics are required. For current IDNA (UTS #46 / IDNA2008) processing, the catalogued ada-url/idna beats ICU at it, and ICU is the general-purpose alternative; both follow the current rules that libidn does not.

## Integration

| | |
|---|---|
| **Form** | shared lib |
| **Dependencies** | none required on glibc; libintl recommended elsewhere; libiconv used for the locale-encoding (_lz) entry points |
| **Minimum toolchain** | ANSI C89 compiler with an autotools build (GNU Make 3.79.1+); Visual Studio 2005+ solution for Windows |
| **Platforms** | GNU/Linux, 20+ other Unix systems, Windows (MinGW or Visual Studio); C# and Java ports included |
| **Thread safety** | Re-entrant: the manual states no global state is kept and no initialization is needed. |
| **Drop-in for the baseline** | partial: libidn2 was built to accept libidn's idna.h calls, so code using only idna_to_ascii_8z-style names can switch back by swapping the header. Code calling idn2_\* functions cannot, and results change for deviation characters such as ß and for post-3.2 code points. |

## Gotchas

- Harness flaw in the only benchmark (addressable PR #496, benchmark/idna.rb): libidn is called through idn-ruby's native C extension, while libidn2 goes through Ruby FFI with a fresh FFI::MemoryPointer, read_string, a separate idn2_free FFI call and force_encoding per call. Part of the 2.4 us per round-trip gap is binding overhead.
- Unequal work in the same harness: libidn runs with IDNA_ALLOW_UNASSIGNED, which skips the unassigned check, while libidn2 runs NONTRANSITIONAL with all IDNA2008 tests. libidn2's idn2_to_unicode_8z8z only punycode-decodes (flags unused, no validation), while libidn's ToUnicode re-runs Nameprep and a full ToASCII round trip. Per-direction costs are therefore not comparable, the script asserts only the to_ascii outputs, and the timings are a 2023 comment pasted into the script (the branch was rebased in May 2026).
- Pass valid UTF-8 only. Release 1.31 began rejecting invalid UTF-8 in stringprep_utf8_to_ucs4 (CVE-2015-2059). Fuzzing-found integer overflows in the Punycode decoder and combine_hangul were fixed in 1.34, and a read out of bounds in the ToUnicode APIs was fixed in 1.44 (2026-06-16). Use 1.44 or later on untrusted input.
- Output strings are malloc'ed and must be freed by the caller. On Windows, free them with idn_free from idn-free.h, because DLLs can use separate heaps.

## Known shortcomings

- Tier C: the addressable PR #496 Ruby benchmark (benchmark/idna.rb, output checked) gives libidn 0.521704 s vs libidn2 0.764863 s per 100k cycles (1.47x; 11.6x vs pure Ruby, derived), but libidn1 is called through the idn-ruby native extension while libidn2 goes through per-call Ruby FFI, so binding cost is mixed into the gap; libidn implements the superseded IDNA2003 and does less work than IDNA2008 plus UTS#46 (its own README tells users to move to libidn2, the baseline); one string; no hardware, Ruby version or compiler; third-party PR open and unmerged since 2023-03-22. Filed under unicode-utf8 by category override; LGPL-3.0-or-later OR GPL-2.0-or-later; 3 stars on the GitLab mirror.
- Enricher (addressable PR #496): libidn is called through the idn-ruby C extension with IDNA_ALLOW_UNASSIGNED while libidn2 goes through Ruby FFI (MemoryPointer, read_string, idn2_free per call) with NONTRANSITIONAL and all checks; libidn2 to_unicode only punycode-decodes while libidn ToUnicode reruns nameprep plus a full ToASCII round trip; the script asserts to_ascii output only; timings are a 2023 comment pasted into the script (branch rebased May 2026). IDNA2003 is superseded (own README says migrate) and outputs differ (faß.de gives fass.de vs xn--fa-hia.de); out-of-bounds read in ToUnicode fixed in 1.44 (2026-06-16).

## Caveats and trade-offs

One input string, wall time through Ruby binding layers rather than raw C calls, and the bindings are not equivalent: libidn (v1) is called through the idn-ruby gem's native C extension, while libidn2 goes through a new Ruby FFI binding that allocates MemoryPointers per call, so part of the 1.47x gap is binding overhead, not library speed. The two libraries also implement different standards: libidn implements the superseded IDNA2003 (Unicode 3.2 nameprep) while libidn2 implements IDNA2008 plus UTS#46, which the PR author says does more work; libidn's own README warns that IDNA2003 is superseded and asks users to migrate to libidn2. No hardware, OS, Ruby version or compiler stated, and the PR (opened 2023-03-22 by jarthod, branch jarthod/addressable:libidn2) is still open and unmerged. The libidn1 vs libidn2 gap is an incidental side result of a wrapper benchmark, not a claim by the libidn project, whose README makes no performance claim. libidn2's own merge request 134 ('punycode decode: slightly faster for common cases', up to 5 percent) compares libidn2 against itself.

Implements IDNA2003 (stringprep, nameprep, punycode, TLD checks) which is obsolete for browsers and registries; libidn2 implements IDNA2008 with UTS #46 compatibility processing and does more work per name, so the speed gap partly reflects fewer checks. Library files are dual LGPL-3.0-or-later or GPL-2.0-or-later (tools GPL-3.0-or-later).

## Maintenance

Maintained by GNU (v1.44 released 2026-06-16 with an out-of-bounds read fix; commits through 2026-08-27) but frozen on a superseded standard that its own README tells users to leave; usable for legacy IDNA2003 and Stringprep needs under LGPL-3.0+/GPL-2.0+.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** The only numbers are an ad-hoc Ruby Benchmark.bmbm run (benchmark/idna.rb) in an open, unmerged third-party PR to the addressable gem; the script is public and checks each backend's to_ascii output against the expected string, but no hardware, OS, Ruby version, compiler or flags are given and it is not a well-known independent suite, so C.
- **Verifier notes:** Numbers on the PR page match the record (rehearsal row) and the script verifies all three backends produce the expected ACE string, so the evidence is valid but weak. Shortcomings to record: unequal bindings (native extension vs per-call FFI) confound the 1.47x libidn-over-libidn2 gap; libidn implements the superseded IDNA2003, so it is faster partly by doing less and is deprecated by its own maintainers in favour of the baseline; single string, no hardware or toolchain, unmerged third-party PR. License (C library LGPL-3.0-or-later OR GPL-2.0-or-later; tools GPL-3.0-or-later), last commit 2026-08-27 and active status confirmed from GitLab.
- **Fields the verifier corrected:** `claimed_speedup`, `stars_or_usage`, `caveats`
- **Shortcomings recorded by:** verifier batch-77 (wave 5); enricher (wave 5)
- **Pages the verifier opened:**
  - <https://github.com/sporkmonger/addressable/pull/496>
  - <https://github.com/sporkmonger/addressable/pull/496/files>
  - <https://gitlab.com/api/v4/projects/libidn%2Flibidn?license=true>
  - <https://gitlab.com/api/v4/projects/libidn%2Flibidn/repository/commits?per_page=3>
  - <https://gitlab.com/libidn/libidn/-/raw/master/README.md>
- **Sources the enricher read:**
  - <https://gitlab.com/libidn/libidn/-/raw/master/README.md>
  - <https://gitlab.com/libidn/libidn/-/raw/master/NEWS>
  - <https://gitlab.com/libidn/libidn/-/raw/master/doc/libidn.texi>
  - <https://gitlab.com/libidn/libidn/-/raw/master/lib/idna.h>
  - <https://gitlab.com/libidn/libidn/-/raw/master/lib/idna.c>
  - <https://gitlab.com/libidn/libidn/-/raw/master/lib/stringprep.c>
  - <https://gitlab.com/libidn/libidn/-/raw/master/lib/nfkc.c>
  - <https://gitlab.com/libidn/libidn/-/raw/master/DEPENDENCIES.md>
  - <https://gitlab.com/libidn/libidn/-/raw/master/configure.ac>
  - <https://gitlab.com/api/v4/projects/libidn%2Flibidn/repository/tags?per_page=3>
  - <https://gitlab.com/libidn/libidn2/-/raw/master/README.md>
  - <https://gitlab.com/libidn/libidn2/-/raw/master/lib/lookup.c>
  - <https://gitlab.com/libidn/libidn2/-/raw/master/lib/decode.c>
  - <https://github.com/sporkmonger/addressable/pull/496>
  - <https://raw.githubusercontent.com/jarthod/addressable/libidn2/benchmark/idna.rb>
  - <https://raw.githubusercontent.com/jarthod/addressable/libidn2/lib/addressable/idna/libidn1.rb>
  - <https://raw.githubusercontent.com/jarthod/addressable/libidn2/lib/addressable/idna/libidn2.rb>
  - <https://raw.githubusercontent.com/jarthod/addressable/libidn2/spec/addressable/idna_spec.rb>
  - <https://raw.githubusercontent.com/deepfryed/idn-ruby/HEAD/ext/idna.c>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://gitlab.com/libidn/libidn`) · [data/wave5/enrich/raw/gitlab_com_libidn_libidn.json](../../../data/wave5/enrich/raw/gitlab_com_libidn_libidn.json) (enrichment confidence 0.75)

</details>
