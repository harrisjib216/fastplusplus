# Wave 7 leads for a seed pass

Candidates surfaced by verifiers and enrichers, not yet in any wave's records.

Seeded as w7-seed-leads (bobjen/spookyhash, pauldreik/lemac).

- bobjen/spookyhash (Bob Jenkins' official SpookyV2 repo, Mar 2026, Unlicense, C++ + Rust): the code the rurban/SMHasher3 SpookyV2 numbers actually measure; the listed g1mv/spookyhash is an archived C port. Candidate replacement link. (from SpookyHash enrichment)
- pauldreik/lemac (C++20 LeMac port with arm64 support) and jedisct1/zig-lemac: maintained LeMac implementations; the listed AugustinBariant repo is stale research code implementing the original LeMac-0 (the ToSC 2025(1) corrigendum fixed a message-schedule mismatch). (from LeMac enrichment)
- RH512 (Antonio García Leal, MIT): 256-bit hash that beats rainbow-256 on SMHasher3 (79.73 cycles, 2.50 B/cycle); source seen only as SMHasher3 hashes/g3-rh512-256.cpp, upstream repo not found (enricher lead, 2026-10-07).
- From w7-mine-e (2026-10-11): BoringSSL VAES AES-GCM commit with Zen 5 tables, briansmith/crypto-bench, aws-lc issue 2283 (cross-library AEAD numbers); sha1collisiondetection is slower than block-sha1 (1.75x) and OpenSSL (2.7x), no record.
- Nettle (w7-mine-d, 2026-10-11): snippet-only 2022 POWER9 Poly1305 patch at 0.972 vs OpenSSL 1.453 cycles/byte on lists.lysator.liu.se (blocked); unverified lead.
- BoringSSL: HAProxy 'State of SSL Stacks' (haproxy.com blocked) is the best lead for independent BoringSSL vs OpenSSL numbers; centminmod page also unreachable.
- Seed-pass verifier lead (2026-10-13): kbench9000 (Donenfeld) shows fiat-crypto's fiat64 about 1.12x faster than donna64 (snippet only; moderncrypto.org and lists.zx2c4.com blocked).
