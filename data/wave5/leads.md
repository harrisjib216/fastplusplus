# Wave 5 leads for a seed pass

Candidates surfaced by verifiers and enrichers, not yet in any wave's records.

- Caladan (https://github.com/shenango/caladan): Shenango's successor, OSDI '20; claims up to 11,000x lower tail latency than Parties. Found by the Shenango verifier.
- milo (https://github.com/ShogunPanda/milo): HTTP/1.1 parser with a C++-vs-llhttp harness but no published numbers. Only if numbers appear.
- Machnet (https://github.com/microsoft/machnet): DPDK messaging for cloud VMs, which the eRPC authors recommend in eRPC's place. Found by the eRPC enricher.
- rsloop: a Python event loop whose benchmark doc compares itself with uvloop and stdlib asyncio (CPython 3.14). Found by the uvloop enricher; picked up by the event-loops hn search, so no seed needed.

Seeded as w5-seed-leads (Caladan, Machnet) on 2026-09-26. milo was found by the http-parsers gh-any search.
- iceoryx2 (eclipse-iceoryx/iceoryx2): Rust core with C/C++ bindings; README benchmark plots vs other IPC on i7-13700H, rustc 1.81, gcc 14.2.1. Not catalogued (enricher lead, 2026-10-07).
- libuv (wave 11, filesystems-and-io, tier D): w5-mine-c found PR 3952 (io_uring 8x over its own thread pool, reverted to opt-in in 1.49.0); libuv is also the event-loops-io incumbent, so a retier of the wave 11 record is the only place for it.
- Asio retier lead: Boost.Redis benchmarks.tex reports an Asio coroutine echo server at 29.5 s vs libuv 43.6 s (1000 sessions x 5000 msgs, no CPU or flags); libhv's shootout has Asio slower than libevent. First-party (Boost), so tier C either way; boostorg/asio mirror from w5-mine-f recorded as duplicate of chriskohlhoff/asio (2026-10-07).
- C++ Actor Framework (https://github.com/actor-framework/actor-framework): paper arXiv 1505.07368 (vs Erlang, Charm++, Akka) blocked; retry from a session with paper access (w5-mine-g, 2026-10-07).
- kovidgoyal/html5-parser (https://github.com/kovidgoyal/html5-parser): gumbo-based Python HTML5 parser, 0.397 s vs 13.906 s html5lib on a 5.7 MB page; gumbo-parser itself (archived 2026-01-21) has no numbers (w5-mine-i, 2026-10-07).
- libev retier lead (https://github.com/enki/libev, event-loops-io, tier C): bartman/event-loop-benchmark README gives libev about 4.5x faster than libevent and libevent 1.36x faster than libuv in the total column; an independent harness that could lift libev to B if its code, flags and CPU check out (w5-mine-k, 2026-10-07). TechEmpower FrameworkBenchmarks has a frameworks/C++/libhttpserver plaintext entry (techempower.com blocked).
- TreeFrog Framework (https://github.com/treefrogframework/treefrog-framework): TechEmpower rounds 9, 13 and 22 rows (round 13 treefrog-thread 312,573 rps, 4.6% of the top, per snippet) on techempower.com (blocked); not faster, no record (w5-mine-q, 2026-10-07).
