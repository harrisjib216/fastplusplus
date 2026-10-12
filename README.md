# fastpp: faster than the default

A catalog of libraries and tools that are measurably faster than the incumbent developers reach for by
default: the C++ standard library, GCC/Clang/ld, zlib, OpenSSL and so on. Every entry names the baseline it
beats, quotes the speedup from its source, and carries an evidence tier. A separate verifier re-checked each
claim against the cited page before it was written up.

## Lists

- [COPYABLE.md](COPYABLE.md): 2689 entries under an OSI license or CC0. Code can be vendored or forked.
- [REFERENCE.md](REFERENCE.md): 263 entries with no, unclear, or non-OSI license. Study the idea; don't copy the code.
- [REJECTED.md](REJECTED.md): 41 candidates that failed verification.

Tiers across both lists: A 594, B 475, C 1638, D 245.

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
| assembly-simd-kernels-and-wasm | asm-level-string-and-memory | 34 | 7 | 0 | 19 | 8 |
| assembly-simd-kernels-and-wasm | assemblers-and-asm-tooling | 32 | 7 | 4 | 15 | 6 |
| assembly-simd-kernels-and-wasm | assemblyscript-and-wasm-langs | 46 | 1 | 0 | 33 | 12 |
| assembly-simd-kernels-and-wasm | hand-written-asm-kernels | 45 | 8 | 0 | 33 | 4 |
| assembly-simd-kernels-and-wasm | simd-intrinsics-libraries | 58 | 10 | 5 | 36 | 7 |
| assembly-simd-kernels-and-wasm | wasm-libraries-and-apps | 73 | 6 | 11 | 42 | 14 |
| assembly-simd-kernels-and-wasm | wasm-runtimes-and-compilers | 6 | 1 | 1 | 3 | 1 |
| compression-and-encoding | entropy-coders | 26 | 2 | 5 | 19 | 0 |
| compression-and-encoding | erasure-codes | 1 | 0 | 0 | 1 | 0 |
| compression-and-encoding | general-lossless | 72 | 26 | 10 | 30 | 6 |
| compression-and-encoding | integer-bitpacking | 24 | 2 | 2 | 19 | 1 |
| compression-and-encoding | succinct-structures | 30 | 8 | 7 | 11 | 4 |
| crypto-and-hashing | aead-and-ciphers | 22 | 8 | 4 | 8 | 2 |
| crypto-and-hashing | crypto-hashes | 16 | 4 | 5 | 6 | 1 |
| crypto-and-hashing | encoding | 26 | 8 | 1 | 17 | 0 |
| crypto-and-hashing | non-crypto-hashes | 31 | 6 | 18 | 7 | 0 |
| crypto-and-hashing | signatures-kem | 22 | 7 | 5 | 10 | 0 |
| interpreters-and-vms | bytecode-vms-and-wasm | 56 | 9 | 16 | 28 | 3 |
| interpreters-and-vms | embedded-scripting | 62 | 6 | 29 | 25 | 2 |
| interpreters-and-vms | jits | 61 | 12 | 11 | 37 | 1 |
| interpreters-and-vms | language-interpreters | 50 | 11 | 10 | 27 | 2 |
| media-and-graphics | color-and-resampling | 62 | 4 | 5 | 45 | 8 |
| media-and-graphics | computer-vision | 1 | 0 | 0 | 1 | 0 |
| media-and-graphics | font-shaping-text-layout | 26 | 1 | 3 | 20 | 2 |
| media-and-graphics | image-codecs | 78 | 19 | 8 | 42 | 9 |
| media-and-graphics | rasterizers-2d | 39 | 2 | 9 | 22 | 6 |
| media-and-graphics | video-audio | 63 | 3 | 4 | 48 | 8 |
| networking-and-servers | dns-quic-http3 | 18 | 0 | 8 | 10 | 0 |
| networking-and-servers | event-loops-io | 42 | 8 | 8 | 25 | 1 |
| networking-and-servers | http-parsers | 25 | 5 | 1 | 18 | 1 |
| networking-and-servers | http-servers-frameworks | 52 | 5 | 22 | 22 | 3 |
| networking-and-servers | tls | 16 | 3 | 4 | 9 | 0 |
| networking-and-servers | websocket-grpc-rpc | 25 | 5 | 2 | 18 | 0 |
| numerics-and-science | autodiff-and-ml-kernels | 102 | 12 | 22 | 66 | 2 |
| numerics-and-science | big-integer-arbitrary-precision | 43 | 10 | 4 | 26 | 3 |
| numerics-and-science | blas-lapack | 61 | 14 | 13 | 26 | 8 |
| numerics-and-science | fft | 49 | 13 | 9 | 21 | 6 |
| numerics-and-science | geometry-spatial | 73 | 5 | 12 | 52 | 4 |
| numerics-and-science | random-and-quasi-random | 61 | 15 | 4 | 39 | 3 |
| numerics-and-science | sparse-and-solvers | 59 | 7 | 25 | 23 | 4 |
| other-languages-faster-than-c-cpp-asm | concurrency-runtimes | 21 | 1 | 1 | 12 | 7 |
| other-languages-faster-than-c-cpp-asm | numerics-and-arrays | 35 | 5 | 0 | 20 | 10 |
| other-languages-faster-than-c-cpp-asm | runtime-jit-beats-aot | 45 | 12 | 0 | 20 | 13 |
| other-languages-faster-than-c-cpp-asm | string-and-text | 57 | 15 | 6 | 29 | 7 |
| other-languages-faster-than-c-cpp-asm | systems-and-safety | 62 | 11 | 2 | 42 | 7 |
| other-languages-faster-than-c-cpp-asm | web-and-serving | 53 | 19 | 7 | 15 | 12 |
| parsing-and-text | csv-tabular | 18 | 4 | 0 | 12 | 2 |
| parsing-and-text | lexers-tokenizers | 10 | 1 | 1 | 7 | 1 |
| parsing-and-text | markup-html-markdown | 11 | 1 | 2 | 8 | 0 |
| parsing-and-text | parser-generators-and-combinators | 12 | 4 | 0 | 7 | 1 |
| parsing-and-text | regex-engines | 12 | 2 | 3 | 7 | 0 |
| parsing-and-text | text-search-and-indexing | 14 | 3 | 1 | 10 | 0 |
| parsing-and-text | unicode-utf8 | 23 | 7 | 0 | 14 | 2 |
| runtime-and-systems | allocators-gcs | 30 | 4 | 4 | 19 | 3 |
| runtime-and-systems | coroutines-fibers | 20 | 0 | 1 | 16 | 3 |
| runtime-and-systems | filesystems-and-io | 48 | 1 | 10 | 34 | 3 |
| runtime-and-systems | logging-tracing | 23 | 14 | 0 | 8 | 1 |
| runtime-and-systems | profilers-and-instrumentation | 20 | 0 | 5 | 10 | 5 |
| runtime-and-systems | thread-pools-work-stealing | 21 | 5 | 2 | 12 | 2 |
| serialization-and-formats | binary-schemas | 53 | 16 | 11 | 25 | 1 |
| serialization-and-formats | json | 69 | 29 | 5 | 32 | 3 |
| serialization-and-formats | reflection-and-codegen | 13 | 3 | 1 | 8 | 1 |
| serialization-and-formats | yaml-toml-xml | 33 | 9 | 2 | 22 | 0 |
| stdlib-replacements | allocators | 18 | 4 | 4 | 9 | 1 |
| stdlib-replacements | async-tasks-threadpools | 8 | 5 | 1 | 1 | 1 |
| stdlib-replacements | bitsets-and-succinct | 7 | 3 | 0 | 4 | 0 |
| stdlib-replacements | concurrency-queues-locks | 9 | 6 | 0 | 3 | 0 |
| stdlib-replacements | graph-algorithms | 2 | 0 | 1 | 1 | 0 |
| stdlib-replacements | hash-maps-sets | 26 | 18 | 1 | 7 | 0 |
| stdlib-replacements | io-and-filesystem | 4 | 1 | 0 | 3 | 0 |
| stdlib-replacements | k-mer-dictionaries | 3 | 1 | 2 | 0 | 0 |
| stdlib-replacements | math-simd-linear-algebra | 24 | 5 | 3 | 14 | 2 |
| stdlib-replacements | minimal-perfect-hash-functions | 20 | 14 | 2 | 4 | 0 |
| stdlib-replacements | number-parsing-formatting | 21 | 8 | 2 | 11 | 0 |
| stdlib-replacements | ordered-maps-trees | 10 | 4 | 0 | 5 | 1 |
| stdlib-replacements | perfect-hash-static-tables | 21 | 9 | 0 | 12 | 0 |
| stdlib-replacements | priority-queues-heaps | 5 | 4 | 0 | 1 | 0 |
| stdlib-replacements | random | 9 | 4 | 2 | 3 | 0 |
| stdlib-replacements | ranges-and-views | 1 | 0 | 0 | 1 | 0 |
| stdlib-replacements | regex | 9 | 3 | 3 | 3 | 0 |
| stdlib-replacements | searching | 6 | 2 | 0 | 4 | 0 |
| stdlib-replacements | sequence-containers | 12 | 3 | 0 | 7 | 2 |
| stdlib-replacements | serialization-json | 17 | 7 | 0 | 9 | 1 |
| stdlib-replacements | small-buffer-and-strings | 15 | 1 | 0 | 11 | 3 |
| stdlib-replacements | smart-pointers-and-refcount | 10 | 3 | 2 | 4 | 1 |
| stdlib-replacements | sorting | 28 | 7 | 0 | 20 | 1 |
| stdlib-replacements | string-search-and-hashing | 10 | 5 | 1 | 4 | 0 |
| stdlib-replacements | utilities | 3 | 0 | 0 | 2 | 1 |
| storage-and-data | caches | 38 | 1 | 17 | 20 | 0 |
| storage-and-data | columnar-analytics | 36 | 4 | 12 | 20 | 0 |
| storage-and-data | database-client-drivers | 1 | 0 | 0 | 1 | 0 |
| storage-and-data | embedded-kv | 51 | 4 | 13 | 31 | 3 |
| storage-and-data | embedded-kv-lsm | 1 | 0 | 0 | 1 | 0 |
| storage-and-data | filters-bloom-cuckoo-xor | 1 | 0 | 1 | 0 | 0 |
| storage-and-data | indexes | 34 | 3 | 20 | 11 | 0 |
| storage-and-data | message-queues-logs | 28 | 2 | 2 | 24 | 0 |
| storage-and-data | probabilistic-filters | 42 | 10 | 12 | 19 | 1 |
| toolchain-and-build | build-systems | 5 | 1 | 0 | 4 | 0 |
| toolchain-and-build | compile-caching-and-distribution | 4 | 0 | 0 | 4 | 0 |
| toolchain-and-build | compilers-frontends | 7 | 1 | 1 | 4 | 1 |
| toolchain-and-build | formatters-linters-lsps | 6 | 3 | 0 | 3 | 0 |
| toolchain-and-build | linkers | 4 | 2 | 1 | 1 | 0 |
| toolchain-and-build | preprocessors-and-codegen | 5 | 0 | 1 | 4 | 0 |

## How entries are made

Search agents look for candidates per domain × category × source; a merge step dedups them; an Opus
verifier opens each cited benchmark and re-derives the tier; a Sonnet enrichment agent reads the repo and
writes the entry. Prompts and rules: [faster-than-std-agent-prompt.md](faster-than-std-agent-prompt.md);
scripts: [pipeline/](pipeline/); raw records: [data/](data/).

Speedups are the authors' or third parties' published numbers. None has been re-run on our own hardware yet
(that is the planned code-audit stage).

Regenerate the lists with `python3 pipeline/render_lists.py`.
