"""Display metadata for the rendered catalog: domain order, titles and intros, category titles, and category
aliases. Data files keep their slugs; only the rendered pages use these names."""

# Domain slug -> (title, one-sentence intro). Order is the order on the index pages: the standard library first,
# then the waves in the order they ran.
DOMAINS = {
    "stdlib-replacements": (
        "C++ standard library replacements",
        "Containers, algorithms and utilities that beat the C++ standard library's own: hash maps, sorting, number "
        "parsing, allocators, regex and more."),
    "toolchain-and-build": (
        "Toolchain and build",
        "Compilers, linkers, build systems and compile caches that turn source into binaries faster than GCC, Clang, "
        "GNU ld, Make or ccache."),
    "parsing-and-text": (
        "Parsing and text",
        "Regex engines, tokenizers, CSV and markup parsers, Unicode transcoders and text search measured against "
        "PCRE2, ICU, grep and their peers."),
    "serialization-and-formats": (
        "Serialization and formats",
        "JSON, YAML, TOML, XML and binary-schema libraries measured against RapidJSON, nlohmann/json, Protobuf and "
        "the other usual defaults."),
    "networking-and-servers": (
        "Networking and servers",
        "HTTP parsers and servers, event loops, TLS, QUIC and RPC stacks measured against nginx, libuv, OpenSSL, "
        "gRPC and friends."),
    "storage-and-data": (
        "Storage and data",
        "Embedded key-value stores, caches, indexes, probabilistic filters, columnar engines and message logs "
        "measured against RocksDB, Redis, Kafka and others."),
    "crypto-and-hashing": (
        "Crypto and hashing",
        "Ciphers, cryptographic and non-cryptographic hashes, signatures and encoders that beat OpenSSL, libsodium "
        "and the common hash functions."),
    "numerics-and-science": (
        "Numerics and science",
        "BLAS, FFT, sparse solvers, big integers, random numbers, geometry and ML kernels measured against MKL, "
        "FFTW, GMP, Eigen and their peers."),
    "compression-and-encoding": (
        "Compression and encoding",
        "Lossless compressors, entropy coders, integer bit-packing and succinct structures that beat zlib, zstd, "
        "lz4 and SDSL."),
    "media-and-graphics": (
        "Media and graphics",
        "Image and video codecs, 2D rasterizers, color conversion, resampling and text shaping measured against "
        "libjpeg-turbo, FFmpeg, Skia and HarfBuzz."),
    "runtime-and-systems": (
        "Runtime and systems",
        "Allocators, coroutines, thread pools, logging, profilers and file I/O measured against malloc, spdlog, "
        "TBB and the POSIX defaults."),
    "interpreters-and-vms": (
        "Interpreters and VMs",
        "Interpreters, JIT compilers, embeddable scripting engines and bytecode VMs measured against CPython, Lua, "
        "V8 and wasmtime."),
    "assembly-simd-kernels-and-wasm": (
        "Assembly, SIMD and WebAssembly",
        "Hand-written assembly, SIMD libraries, assemblers and WebAssembly toolchains measured against compiler "
        "output, libc routines and native builds."),
    "other-languages-faster-than-c-cpp-asm": (
        "Other languages beating C, C++ and assembly",
        "Benchmarks where Rust, Zig, Julia, Go, Java and other languages beat the same task written in C, C++ or "
        "assembly, with the mechanism behind each win."),
}

CATEGORY_TITLES = {
    # stdlib-replacements
    "allocators": "Allocators",
    "async-tasks-threadpools": "Async tasks and thread pools",
    "bitsets-and-succinct": "Bitsets and succinct bit vectors",
    "concurrency-queues-locks": "Concurrent queues and locks",
    "graph-algorithms": "Graph algorithms",
    "hash-maps-sets": "Hash maps and sets",
    "io-and-filesystem": "I/O and filesystem",
    "k-mer-dictionaries": "k-mer dictionaries",
    "math-simd-linear-algebra": "Math, SIMD and linear algebra",
    "minimal-perfect-hash-functions": "Minimal perfect hash functions",
    "number-parsing-formatting": "Number parsing and formatting",
    "ordered-maps-trees": "Ordered maps and trees",
    "perfect-hash-static-tables": "Perfect hashing and static tables",
    "priority-queues-heaps": "Priority queues and heaps",
    "random": "Random numbers",
    "ranges-and-views": "Ranges and views",
    "regex": "Regex",
    "searching": "Searching",
    "sequence-containers": "Sequence containers",
    "serialization-json": "JSON serialization",
    "small-buffer-and-strings": "Small-buffer containers and strings",
    "smart-pointers-and-refcount": "Smart pointers and reference counting",
    "sorting": "Sorting",
    "string-search-and-hashing": "String search and hashing",
    "utilities": "Utilities",
    # toolchain-and-build
    "build-systems": "Build systems",
    "compile-caching-and-distribution": "Compile caching and distribution",
    "compilers-frontends": "Compilers and front ends",
    "formatters-linters-lsps": "Formatters, linters and language servers",
    "linkers": "Linkers",
    "preprocessors-and-codegen": "Preprocessors and code generators",
    # parsing-and-text
    "csv-tabular": "CSV and tabular data",
    "lexers-tokenizers": "Lexers and tokenizers",
    "markup-html-markdown": "HTML, Markdown and markup",
    "parser-generators-and-combinators": "Parser generators and combinators",
    "regex-engines": "Regex engines",
    "text-search-and-indexing": "Text search and indexing",
    "unicode-utf8": "Unicode and UTF-8",
    # serialization-and-formats
    "binary-schemas": "Binary schemas",
    "json": "JSON",
    "reflection-and-codegen": "Reflection and code generation",
    "yaml-toml-xml": "YAML, TOML and XML",
    # networking-and-servers
    "dns-quic-http3": "DNS, QUIC and HTTP/3",
    "event-loops-io": "Event loops and async I/O",
    "http-parsers": "HTTP parsers",
    "http-servers-frameworks": "HTTP servers and frameworks",
    "tls": "TLS",
    "websocket-grpc-rpc": "WebSocket, gRPC and RPC",
    # storage-and-data
    "caches": "Caches",
    "columnar-analytics": "Columnar analytics",
    "database-client-drivers": "Database client drivers",
    "embedded-kv": "Embedded key-value stores",
    "indexes": "Indexes",
    "message-queues-logs": "Message queues and logs",
    "probabilistic-filters": "Probabilistic filters",
    # crypto-and-hashing
    "aead-and-ciphers": "AEAD and ciphers",
    "crypto-hashes": "Cryptographic hashes",
    "encoding": "Encoding (base64, hex, CRC)",
    "non-crypto-hashes": "Non-cryptographic hashes",
    "signatures-kem": "Signatures and key exchange",
    # numerics-and-science
    "autodiff-and-ml-kernels": "Autodiff and ML kernels",
    "big-integer-arbitrary-precision": "Big integers and arbitrary precision",
    "blas-lapack": "BLAS and LAPACK",
    "fft": "FFT",
    "geometry-spatial": "Geometry and spatial",
    "random-and-quasi-random": "Random and quasi-random numbers",
    "sparse-and-solvers": "Sparse matrices and solvers",
    # compression-and-encoding
    "entropy-coders": "Entropy coders",
    "erasure-codes": "Erasure codes",
    "general-lossless": "General-purpose lossless compression",
    "integer-bitpacking": "Integer compression and bit-packing",
    "succinct-structures": "Succinct data structures",
    # media-and-graphics
    "color-and-resampling": "Color conversion and resampling",
    "computer-vision": "Computer vision",
    "font-shaping-text-layout": "Font shaping and text layout",
    "image-codecs": "Image codecs",
    "rasterizers-2d": "2D rasterizers",
    "video-audio": "Video and audio",
    # runtime-and-systems
    "allocators-gcs": "Allocators and garbage collectors",
    "coroutines-fibers": "Coroutines and fibers",
    "filesystems-and-io": "Filesystems and I/O",
    "logging-tracing": "Logging and tracing",
    "profilers-and-instrumentation": "Profilers and instrumentation",
    "thread-pools-work-stealing": "Thread pools and work stealing",
    # interpreters-and-vms
    "bytecode-vms-and-wasm": "Bytecode VMs and WebAssembly runtimes",
    "embedded-scripting": "Embedded scripting",
    "jits": "JIT compilers",
    "language-interpreters": "Language interpreters",
    # assembly-simd-kernels-and-wasm
    "asm-level-string-and-memory": "Assembly-level string and memory routines",
    "assemblers-and-asm-tooling": "Assemblers and assembly tooling",
    "assemblyscript-and-wasm-langs": "AssemblyScript and WebAssembly languages",
    "hand-written-asm-kernels": "Hand-written assembly kernels",
    "simd-intrinsics-libraries": "SIMD intrinsics libraries",
    "wasm-libraries-and-apps": "WebAssembly libraries and apps",
    "wasm-runtimes-and-compilers": "WebAssembly runtimes and compilers",
    # other-languages-faster-than-c-cpp-asm
    "concurrency-runtimes": "Concurrency runtimes",
    "numerics-and-arrays": "Numerics and arrays",
    "runtime-jit-beats-aot": "Runtime JIT beats ahead-of-time",
    "string-and-text": "Strings and text",
    "systems-and-safety": "Systems and safety",
    "web-and-serving": "Web and serving",
}

# Single-entry categories created by category overrides that duplicate a neighbour; rendered under the neighbour.
CATEGORY_ALIASES = {
    "embedded-kv-lsm": "embedded-kv",
    "filters-bloom-cuckoo-xor": "probabilistic-filters",
}

# Baseline wording for the domain whose categories share one baseline (spec Part 4, wave 14).
CROSS_LANGUAGE_DOMAIN = "other-languages-faster-than-c-cpp-asm"
CROSS_LANGUAGE_BASELINE = "the same task written in C or C++ at -O3, or hand-written assembly where the source " \
                          "compares against it"

# README highlights: well-known tier A entries, about one per domain (ids from the verified records). Stars alone
# pick sub-components of large monorepos, so this list is chosen by hand; the renderer skips ids that are gone.
FEATURED = [
    "https://github.com/abseil/abseil-cpp",
    "https://github.com/google/highway",
    "https://github.com/microsoft/mimalloc",
    "https://github.com/rui314/mold",
    "https://github.com/quickwit-oss/tantivy",
    "https://github.com/simdjson/simdjson",
    "https://github.com/rustls/rustls",
    "https://github.com/fastfilter/xor_singleheader",
    "https://github.com/cyan4973/xxhash",
    "https://github.com/dao-ailab/flash-attention",
    "https://github.com/google/snappy",
    "https://github.com/phoboslab/qoi",
    "https://github.com/odygrd/quill",
    "https://github.com/ruby/ruby",
    "https://github.com/icedland/iced",
    "lang:rust/kostya/langarena#sort-self",
]
