# Nail (NailDNS demo server)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Networking and servers](../README.md) › [DNS, QUIC and HTTP/3](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `C` · `MIT` · 🔴 abandoned

> 295-line C authoritative DNS demo built on the Nail parser generator; \~2.9x BIND 9.9.5 qps in a 2014 loopback test.

| | |
|---|---|
| **Beats** | BIND |
| **Claimed result** | median throughput \~139,215 qps (NailDNS) vs \~47,234 qps (BIND 9.9.5 per the paper text; the figure caption says 9.5.5), \~2.9x faster (derived from page data); median round-trip time 0.139 ms vs 0.416 ms (derived from page data, box plot of 7 runs each) |
| **Workload** | Authoritative-DNS load test. 50,000 random dictionary-based domains (com/net/org), \~90% of them written to the zone file, so \~10% of queries get NXDOMAIN. Each domain is queried 0-3 times (per the paper) in shuffled order with BIND's queryperf, at most 20 outstanding queries, for 60 s. 7 runs with a daemon restart between runs, against ISC BIND 9.9.5 on the same local machine, one core. |
| **Metric** | throughput |
| **Hardware** | Intel i7-3610QM, single core, 12GB RAM (OSDI'14 paper, Performance subsection) |
| **Compiler and flags** | NailDNS C server built with -std=gnu99 -O3 (examples/dns/Makefile); compiler not named (make default CC); BIND 9.9.5 build flags not stated |
| **Adoption** | 129 stars |
| **Last commit** | 2015-08-17 |
| **Links** | [repository](https://github.com/jbangert/nail) · [benchmark](https://github.com/jbangert/nail/blob/master/paper/osdi14/performance.tex) |

## Verdict

On one core of an Intel i7-3610QM over loopback, BIND's queryperf (at most 20 outstanding, 60 s, 7 runs each, April 2014, 0 lost queries) against a 50,000-name A-record zone with \~10% NXDOMAIN gave a median 139,215 qps for NailDNS vs 47,235 qps for BIND 9.9.5 (\~2.9x), and mean RTT 0.139 ms vs 0.416 ms. NailDNS was built with -std=gnu99 -O3 on an unnamed compiler; BIND's build flags, thread count and named.conf are not published.

## Use it when

- Reproducing or studying the OSDI'14 result: grammar-generated parsing on a small static A-record zone, queried over loopback UDP on one core.
- Learning how to express DNS wire format (count fields, label compression via a stream transform) as a declarative grammar that yields both a parser and a serializer.
- A throwaway, fast stub responder for load-testing DNS clients in a lab, where the zone is a few MB of lowercase A/NS/CNAME names and RFC corner cases do not matter.
- A starting point to copy for a tiny embedded authoritative responder, if you are prepared to fix the known compression and leak bugs yourself.

## Skip it when

- Any production or Internet-facing authoritative service: UDP only, no TCP fallback, never sets TC, no EDNS, no SOA/authority section, no DNSSEC, zone transfer, NOTIFY or TSIG, and the listen address is hard-coded to 127.0.0.1:53.
- Untrusted input: the compression-pointer decoder can spin forever (issue #7; AFL-found hangs, fix PR #10 unmerged), generated code has an integer underflow that loops on short input (issue #9), and every malformed packet leaks its arena and output buffer because the error path skips the release calls.
- Multi-core throughput: the server is a single blocking recvfrom loop with no threads or sockets sharding.
- Real zones: the zone grammar accepts only lowercase a-z and 0-9 in names (no hyphens), only A/NS/MX/CNAME records, not RFC 1035 master-file syntax, and server.c reads at most 4 MiB of zone file (ZONESIZ).
- Anything needing a working, maintained toolchain: no commits since 2015, and open issues report the examples fail with 'Syntax error in grammar' and the tests do not compile.

## How it is fast

It does very little per packet: one thread in a blocking recvfrom/sendto loop, a per-packet bump-pointer arena (NailArena, 4 KiB blocks, freed in one call), and one lookup in an open-addressing hash table (djb2 hash, linear probing, 1.5x zone-count slots) built once at startup. Parsing and response serialization are generated top-down (PEG-style) C that bounds-checks each read and binds fields straight into plain structs; the paper describes a two-pass design (validate while recording a trace, then bind into the arena). No ACL, view, logging, or DNSSEC work sits on the hot path, and the paper itself only claims Nail's parsers are 'not a barrier to achieving good performance', not that they cause the speedup.

## Compared with alternatives

Unbound and Hickory DNS are complete DNS servers, and Bundy-DNS's l1cache branch reports a comparable \~4x-over-BIND gain (180K vs 41K qps) from pre-rendered answers. Pick NailDNS only to study or reuse grammar-generated DNS parsing or as a disposable lab responder; for actual serving pick one of those siblings by role.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | Generator: C++11 compiler (Makefile hard-codes clang/clang++), Boost, xxd; example Makefiles also call astyle. Generated C uses libc (malloc/realloc/memset) and setjmp/longjmp despite the README saying it uses no standard library. Server: POSIX sockets and err.h. |
| **Minimum toolchain** | C gnu99 for the examples (generator C parts gnu11), C++11 for the generator; generated code uses GCC/Clang extensions (__builtin_expect, typeof). |
| **Platforms** | Linux/POSIX UDP (author used Arch and Ubuntu); benchmarked only on x86-64. macOS builds needed the 2015 switch from GNU ld --format=binary to xxd (issue #2). |
| **Thread safety** | not documented; the demo server is single-threaded and parsers take caller-owned arenas |
| **Drop-in for the baseline** | no |

## Gotchas

- Name matching is a case-sensitive memcmp plus a djb2 hash over raw bytes, so mixed-case queries (for example DNS 0x20 case randomization) get NXDOMAIN; a name that exists with a different record type also gets NXDOMAIN instead of NODATA.
- The decompressor computes pointers as `highbyte & 63 << 8 | ...`, which drops the high 6 offset bits, and it has no loop limit; the paper's 4-hour Metasploit fuzz run did not catch it, but AFL did (PR #10).
- MX answers carry only the target name with no 16-bit preference field, and every answer uses a hard-coded 60 s TTL.
- The 2015 thesis reports a faster C++-backend NailDNS (median \~190.7K qps), but its BIND column is the identical 2014 data, not a fresh head-to-head run.

## Known shortcomings

- A 2014 research demo DNS server (OSDI '14 Nail parser generator), not a production resolver; compared against BIND 9.9.5 on one laptop core. Abandoned since 2015-08. No compiler or BIND build stated.
- BIND configuration, thread count and build flags are not in the repo; an OSDI reviewer called the BIND comparison not apples-to-apples. The thesis 4.0x figure reuses the 2014 BIND column. Security: compression-pointer decoder precedence bug and no loop limit (#7, AFL hangs, fix PR #10 unmerged since 2020); generated stream_check can underflow and loop (#9); arena leaked per malformed packet. Demo server binds 127.0.0.1 only, no TCP/truncation, case-sensitive names, NXDOMAIN instead of NODATA, MX without preference, no hyphens in names, 4 MiB zone limit. Examples and tests fail to build (#5, #6, 2015).

## Caveats and trade-offs

Peer-reviewed OSDI'14 paper (USENIX, MIT CSAIL authors). The paper states the CPU (i7-3610QM, one core) and the repo ships the benchmark scripts, queryperf and raw results (examples/dns/bench), but the C compiler and BIND's build are unstated, so the tier is B, not A. The paper body says BIND 9.9.5 (2014), but the figure caption says 9.5.5, probably a caption typo. NailDNS is a minimal 183-line demo server that lacks many BIND features, and the test ran over loopback on one machine. Last commit was 2015 (abandoned).

NailDNS is a 295-line research demo built to showcase the Nail parser-combinator toolkit (grammar-driven parsing/generation with dependent fields and stream transforms); it implements only zone parsing, query answering, and label compression, none of BIND's dynamic reconfiguration, TSIG, notify, or DNSSEC-signing machinery. Not a drop-in BIND replacement.

## Maintenance

Abandoned since 2015-08-17 with the compression-hang fix (PR #10) unmerged since 2020; MIT-licensed and small enough to copy, but expect to repair the build and the DNS-compression code yourself.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed OSDI'14 paper (Bangert & Zeldovich). The published text names an Intel i7-3610QM (one core, 12GB RAM), and the repo ships the benchmark code (examples/dns/bench: random-domains.rb, queryperf, results.50000/all.qps) plus -std=gnu99 -O3 in examples/dns/Makefile. It is not A because the C compiler is never named (make's default CC) and BIND's build is not described.
- **Verifier notes:** The record said no CPU model is stated anywhere and that the baseline is BIND 9.5.5 from 2009. In fact the published paper and eval.tex state an i7-3610QM and BIND 9.9.5; both are corrected. The record's last_commit 2020-07-27 was the repo's pushed_at date: the only branch (master) last committed on 2015-08-17. Usability is changed to copyable per the MIT-license rule, and the demo-server nature is kept in caveats. The medians were re-derived from the fig-perf-dns data, which matches results.50000/all.qps.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `hardware`, `compiler_and_flags`, `last_commit`, `usability`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/jbangert/nail/blob/master/paper/osdi14/performance.tex>
  - <https://github.com/jbangert/nail>
  - <https://github.com/jbangert/nail/blob/master/paper/osdi14/eval.tex>
  - <https://github.com/jbangert/nail/blob/master/paper/osdi14/fig-perf-dns.tex>
  - <https://github.com/jbangert/nail/blob/master/paper/osdi14/impl.tex>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/Makefile>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/bench/random-domains.rb>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/bench/results.50000/all.qps>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/bench/results.50000/all.rttavg>
  - <https://github.com/jbangert/nail/blob/master/examples/dns_cpp/Makefile>
  - <https://github.com/jbangert/nail/blob/master/generator/Makefile>
  - <https://www.usenix.org/conference/osdi14/technical-sessions/presentation/bangert>
  - <https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-bangert.pdf>
- **Sources the enricher read:**
  - <https://github.com/jbangert/nail>
  - <https://github.com/jbangert/nail/blob/master/README.md>
  - <https://github.com/jbangert/nail/blob/master/LICENSE>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/Makefile>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/server.c>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/server.h>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/common.h>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/dns.c>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/dns.nail>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/bench/random-domains.rb>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/bench/extract.sh>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/bench/results.50000/all.qps>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/bench/results.50000/all.rttavg>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/bench/results.50000/naildns.results.60>
  - <https://github.com/jbangert/nail/blob/master/examples/dns/bench/results.50000/named.results.60>
  - <https://github.com/jbangert/nail/blob/master/examples/dns_cpp/Makefile>
  - <https://github.com/jbangert/nail/blob/master/examples/dns_cpp/server.cc>
  - <https://github.com/jbangert/nail/blob/master/examples/dns_cpp/bench/run-benchmark.sh>
  - <https://github.com/jbangert/nail/blob/master/examples/dns_cpp/bench/run-naildns.sh>
  - <https://github.com/jbangert/nail/blob/master/examples/dns_cpp/dns/dns.nail.c>
  - <https://github.com/jbangert/nail/blob/master/generator/Makefile>
  - <https://github.com/jbangert/nail/blob/master/generator/parser_template.c>
  - <https://github.com/jbangert/nail/blob/master/generator/parser_template.h>
  - <https://github.com/jbangert/nail/blob/master/paper/osdi14/performance.tex>
  - <https://github.com/jbangert/nail/blob/master/paper/osdi14/fig-perf-dns.tex>
  - <https://github.com/jbangert/nail/blob/master/paper/osdi14/eval.tex>
  - <https://github.com/jbangert/nail/blob/master/paper/osdi14/impl.tex>
  - <https://github.com/jbangert/nail/blob/master/paper/osdi14/osdi14-reviews.txt>
  - <https://github.com/jbangert/nail/blob/master/paper/osdi14/review_answers.txt>
  - <https://github.com/jbangert/nail/blob/master/paper/thesis/fig-perf-dns.tex>
  - <https://github.com/jbangert/nail/blob/master/paper/thesis/eval.tex>
  - <https://github.com/jbangert/nail/blob/master/paper/thesis/impl.tex>
  - <https://github.com/jbangert/nail/tree/master/paper/login>
  - <https://github.com/jbangert/nail/tree/master/paper/langsec14>
  - <https://github.com/jbangert/nail/issues/2>
  - <https://github.com/jbangert/nail/issues/3>
  - <https://github.com/jbangert/nail/issues/4>
  - <https://github.com/jbangert/nail/issues/5>
  - <https://github.com/jbangert/nail/issues/6>
  - <https://github.com/jbangert/nail/issues/7>
  - <https://github.com/jbangert/nail/issues/9>
  - <https://github.com/jbangert/nail/pull/10>
  - <https://www.usenix.org/conference/osdi14/technical-sessions/presentation/bangert>
- **Raw records:** [data/wave5/verified.json](../../../data/wave5/verified.json) (id `https://github.com/jbangert/nail`) · [data/wave5/enrich/raw/github_com_jbangert_nail.json](../../../data/wave5/enrich/raw/github_com_jbangert_nail.json) (enrichment confidence 0.8)

</details>
