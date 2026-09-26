# Wave 5 leads for a seed pass

Candidates surfaced by verifiers and enrichers, not yet in any wave's records.

- Caladan (https://github.com/shenango/caladan): Shenango's successor, OSDI '20; claims up to 11,000x lower tail latency than Parties. Found by the Shenango verifier.
- milo (https://github.com/ShogunPanda/milo): HTTP/1.1 parser with a C++-vs-llhttp harness but no published numbers. Only if numbers appear.
- Machnet (https://github.com/microsoft/machnet): DPDK messaging for cloud VMs, which the eRPC authors recommend in eRPC's place. Found by the eRPC enricher.
- rsloop: a Python event loop whose benchmark doc compares itself with uvloop and stdlib asyncio (CPython 3.14). Found by the uvloop enricher; picked up by the event-loops hn search, so no seed needed.

Seeded as w5-seed-leads (Caladan, Machnet) on 2026-09-26. milo was found by the http-parsers gh-any search.
