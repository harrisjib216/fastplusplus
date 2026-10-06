# fastpp: faster than the default

A catalog of libraries and tools that are measurably faster than the incumbent developers reach for by
default: the C++ standard library, GCC/Clang/ld, zlib, OpenSSL and so on. Every entry names the baseline it
beats, quotes the speedup from its source, and carries an evidence tier. A separate verifier re-checked each
claim against the cited page before it was written up.

## Lists

- [COPYABLE.md](COPYABLE.md): 1883 entries under an OSI license or CC0. Code can be vendored or forked.
- [REFERENCE.md](REFERENCE.md): 199 entries with no, unclear, or non-OSI license. Study the idea; don't copy the code.
- [REJECTED.md](REJECTED.md): 34 candidates that failed verification.

Tiers across both lists: A 446, B 394, C 1149, D 93.

## Evidence tiers

- **A**: public benchmark code, run against the named baseline, with compiler, flags and CPU model all stated
  (whoever ran it).
- **B**: peer-reviewed paper or well-known independent benchmark suite that falls short of A.
- **C**: numbers from the project itself without full methodology, or numbers without methodology. Listed under
  *Unverified claims*.
- **D**: no numbers; kept only for notable projects.

Ratios marked "(derived from page data)" were computed from numbers on the cited page, not quoted.

## Coverage

| Domain | Category | Entries | A | B | C | D |
|---|---|---|---|---|---|---|
| compression-and-encoding | entropy-coders | 26 | 2 | 5 | 19 | 0 |
| compression-and-encoding | general-lossless | 62 | 22 | 10 | 27 | 3 |
| compression-and-encoding | integer-bitpacking | 24 | 2 | 2 | 19 | 1 |
| compression-and-encoding | succinct-structures | 30 | 8 | 7 | 11 | 4 |
| crypto-and-hashing | aead-and-ciphers | 17 | 7 | 4 | 6 | 0 |
| crypto-and-hashing | crypto-hashes | 16 | 4 | 5 | 6 | 1 |
| crypto-and-hashing | encoding | 25 | 8 | 1 | 16 | 0 |
| crypto-and-hashing | non-crypto-hashes | 30 | 6 | 17 | 7 | 0 |
| crypto-and-hashing | signatures-kem | 20 | 7 | 5 | 8 | 0 |
| interpreters-and-vms | bytecode-vms-and-wasm | 53 | 8 | 15 | 27 | 3 |
| interpreters-and-vms | embedded-scripting | 56 | 6 | 27 | 21 | 2 |
| interpreters-and-vms | jits | 57 | 12 | 10 | 34 | 1 |
| interpreters-and-vms | language-interpreters | 50 | 11 | 10 | 27 | 2 |
| media-and-graphics | color-and-resampling | 57 | 4 | 5 | 42 | 6 |
| media-and-graphics | font-shaping-text-layout | 23 | 1 | 2 | 18 | 2 |
| media-and-graphics | image-codecs | 72 | 17 | 6 | 40 | 9 |
| media-and-graphics | rasterizers-2d | 33 | 2 | 6 | 20 | 5 |
| media-and-graphics | unicode-utf8 | 3 | 0 | 0 | 2 | 1 |
| media-and-graphics | video-audio | 58 | 3 | 3 | 45 | 7 |
| networking-and-servers | dns-quic-http3 | 16 | 0 | 6 | 10 | 0 |
| networking-and-servers | event-loops-io | 36 | 6 | 7 | 23 | 0 |
| networking-and-servers | http-parsers | 23 | 5 | 1 | 17 | 0 |
| networking-and-servers | http-servers-frameworks | 36 | 4 | 20 | 12 | 0 |
| networking-and-servers | tls | 16 | 3 | 4 | 9 | 0 |
| networking-and-servers | websocket-grpc-rpc | 22 | 5 | 2 | 15 | 0 |
| numerics-and-science | autodiff-and-ml-kernels | 81 | 12 | 16 | 52 | 1 |
| numerics-and-science | big-integer-arbitrary-precision | 41 | 10 | 3 | 25 | 3 |
| numerics-and-science | blas-lapack | 55 | 14 | 12 | 23 | 6 |
| numerics-and-science | fft | 46 | 12 | 9 | 19 | 6 |
| numerics-and-science | geometry-spatial | 62 | 5 | 9 | 45 | 3 |
| numerics-and-science | random-and-quasi-random | 59 | 15 | 4 | 37 | 3 |
| numerics-and-science | sparse-and-solvers | 55 | 7 | 25 | 20 | 3 |
| parsing-and-text | csv-tabular | 12 | 2 | 0 | 10 | 0 |
| parsing-and-text | lexers-tokenizers | 9 | 1 | 1 | 6 | 1 |
| parsing-and-text | markup-html-markdown | 9 | 1 | 0 | 8 | 0 |
| parsing-and-text | parser-generators-and-combinators | 8 | 3 | 0 | 5 | 0 |
| parsing-and-text | regex-engines | 10 | 2 | 3 | 5 | 0 |
| parsing-and-text | text-search-and-indexing | 10 | 3 | 0 | 7 | 0 |
| parsing-and-text | unicode-utf8 | 16 | 6 | 0 | 10 | 0 |
| runtime-and-systems | allocators-gcs | 28 | 4 | 4 | 18 | 2 |
| runtime-and-systems | coroutines-fibers | 18 | 0 | 1 | 14 | 3 |
| runtime-and-systems | filesystems-and-io | 46 | 1 | 9 | 33 | 3 |
| runtime-and-systems | logging-tracing | 16 | 11 | 0 | 5 | 0 |
| runtime-and-systems | profilers-and-instrumentation | 20 | 0 | 5 | 10 | 5 |
| runtime-and-systems | thread-pools-work-stealing | 16 | 3 | 1 | 11 | 1 |
| serialization-and-formats | binary-schemas | 48 | 15 | 11 | 22 | 0 |
| serialization-and-formats | json | 52 | 22 | 3 | 26 | 1 |
| serialization-and-formats | reflection-and-codegen | 8 | 3 | 1 | 4 | 0 |
| serialization-and-formats | yaml-toml-xml | 28 | 9 | 0 | 19 | 0 |
| stdlib-replacements | allocators | 17 | 4 | 4 | 8 | 1 |
| stdlib-replacements | async-tasks-threadpools | 8 | 5 | 1 | 1 | 1 |
| stdlib-replacements | bitsets-and-succinct | 6 | 3 | 0 | 3 | 0 |
| stdlib-replacements | concurrency-queues-locks | 8 | 6 | 0 | 2 | 0 |
| stdlib-replacements | hash-maps-sets | 19 | 13 | 1 | 5 | 0 |
| stdlib-replacements | io-and-filesystem | 4 | 1 | 0 | 3 | 0 |
| stdlib-replacements | k-mer-dictionaries | 3 | 1 | 2 | 0 | 0 |
| stdlib-replacements | math-simd-linear-algebra | 10 | 2 | 2 | 5 | 1 |
| stdlib-replacements | minimal-perfect-hash-functions | 20 | 14 | 2 | 4 | 0 |
| stdlib-replacements | number-parsing-formatting | 16 | 6 | 2 | 8 | 0 |
| stdlib-replacements | ordered-maps-trees | 9 | 4 | 0 | 5 | 0 |
| stdlib-replacements | perfect-hash-static-tables | 20 | 8 | 0 | 12 | 0 |
| stdlib-replacements | priority-queues-heaps | 5 | 4 | 0 | 1 | 0 |
| stdlib-replacements | random | 9 | 4 | 2 | 3 | 0 |
| stdlib-replacements | regex | 7 | 3 | 1 | 3 | 0 |
| stdlib-replacements | searching | 6 | 2 | 0 | 4 | 0 |
| stdlib-replacements | sequence-containers | 5 | 2 | 0 | 3 | 0 |
| stdlib-replacements | serialization-json | 10 | 5 | 0 | 5 | 0 |
| stdlib-replacements | small-buffer-and-strings | 8 | 1 | 0 | 6 | 1 |
| stdlib-replacements | smart-pointers-and-refcount | 7 | 3 | 1 | 3 | 0 |
| stdlib-replacements | sorting | 18 | 6 | 0 | 12 | 0 |
| stdlib-replacements | string-search-and-hashing | 9 | 5 | 1 | 3 | 0 |
| storage-and-data | caches | 38 | 1 | 17 | 20 | 0 |
| storage-and-data | columnar-analytics | 33 | 4 | 12 | 17 | 0 |
| storage-and-data | embedded-kv | 41 | 4 | 12 | 25 | 0 |
| storage-and-data | embedded-kv-lsm | 1 | 0 | 0 | 1 | 0 |
| storage-and-data | filters-bloom-cuckoo-xor | 1 | 0 | 1 | 0 | 0 |
| storage-and-data | indexes | 33 | 3 | 20 | 10 | 0 |
| storage-and-data | message-queues-logs | 28 | 2 | 2 | 24 | 0 |
| storage-and-data | probabilistic-filters | 42 | 10 | 12 | 19 | 1 |
| toolchain-and-build | build-systems | 5 | 1 | 0 | 4 | 0 |
| toolchain-and-build | compile-caching-and-distribution | 4 | 0 | 0 | 4 | 0 |
| toolchain-and-build | compilers-frontends | 4 | 0 | 1 | 3 | 0 |
| toolchain-and-build | formatters-linters-lsps | 6 | 3 | 0 | 3 | 0 |
| toolchain-and-build | linkers | 3 | 2 | 0 | 1 | 0 |
| toolchain-and-build | preprocessors-and-codegen | 5 | 0 | 1 | 4 | 0 |

## How entries are made

Search agents look for candidates per domain × category × source; a merge step dedups them; an Opus
verifier opens each cited benchmark and re-derives the tier; a Sonnet enrichment agent reads the repo and
writes the entry. Prompts and rules: [faster-than-std-agent-prompt.md](faster-than-std-agent-prompt.md);
scripts: [pipeline/](pipeline/); raw records: [data/](data/).

Speedups are the authors' or third parties' published numbers. None has been re-run on our own hardware yet
(that is the planned code-audit stage).

Regenerate the lists with `python3 pipeline/render_lists.py`.
