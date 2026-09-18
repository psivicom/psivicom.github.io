Network Working Group                                     L-P. Audette
Request for Comments: 1001                                     PSIVI.COM
Category: Informational                                   September 2026
ISSN: 2070-1721


                    Pico Service Container (.psvc) Format
                 For Decentralized Neuroplastic AI Meshes

Abstract

   This document specifies the Pico Service Container (.psvc) format, a
   lightweight, cryptographically verifiable binary protocol designed
   for the storage, transmission, and execution of high-dimensional
   vector embeddings in decentralized AI meshes. The format is optimized
   for extreme edge compute, volunteer VRAM sharing, and zero-cost
   Git-based memory buses. By utilizing a strict 14-byte header and
   maximum-ratio zlib compression, .psvc containers reduce vector
   storage footprints by up to 90% while maintaining deterministic
   decompression for real-time neuroplastic inference.

Status of This Memo

   This memo provides information for the research and open-science
   community. It defines the standard for the PSIVI Mesh Pico AI
   architecture. Distribution is unlimited.

Copyright Notice

   Copyright (c) 2026 Louis-Philippe Audette | PSIVI.COM
   
   Code and protocol specifications are licensed under the European
   Union Public License (EUPL) v. 1.2.
   Documentation and metadata schemas are licensed under the Creative
   Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).
   Hardware implementations remain proprietary (w-1-n.com).

Table of Contents

   1.  Introduction  . . . . . . . . . . . . . . . . . . . . . . . .   2
   2.  Terminology . . . . . . . . . . . . . . . . . . . . . . . . .   2
   3.  Container Structure . . . . . . . . . . . . . . . . . . . . .   3
   4.  Precision Profiles  . . . . . . . . . . . . . . . . . . . . .   4
   5.  Cryptographic Integrity and Sidecars  . . . . . . . . . . . .   5
   6.  Security Considerations . . . . . . . . . . . . . . . . . . .   6
   7.  IANA Considerations . . . . . . . . . . . . . . . . . . . . .   6
   8.  References  . . . . . . . . . . . . . . . . . . . . . . . . .   6
   9.  Author's Address  . . . . . . . . . . . . . . . . . . . . . .   7

1. Introduction

   Modern AI inference pipelines rely on heavy, proprietary binary
   formats (e.g., Safetensors, GGUF, ONNX) that require gigabytes of
   VRAM and centralized cloud infrastructure. The Mesh Pico AI
   introduces a paradigm shift: decentralized, neuroplastic intelligence
   running on volunteer hardware and Git-based memory buses.

   The .psvc (Pico Service Container) format was created to serve as the
   atomic unit of this mesh. It is designed to be sealed (compressed and
   dormant on disk), portable (transferred via Git push/pull), and
   opened (decompressed directly into active VRAM) only when explicitly
   called by the mesh router.

2. Terminology

   The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
   "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this
   document are to be interpreted as described in RFC 2119.

   - Mesh: The decentralized network of volunteer nodes processing data.
   - Container: A single .psvc binary file.
   - VRAM: Video Random Access Memory, used for active vector math.
   - Cortex: The neuroplastic agent responsible for clustering vectors.
   - Pico Limit: The strict maximum number of containers allowed in
     active VRAM simultaneously (typically 5).

3. Container Structure

   A .psvc container consists of a fixed 14-byte header followed by a
   variable-length zlib-compressed payload. All multi-byte integers in
   the header MUST be encoded in Little-Endian byte order to align with
   standard x86_64 volunteer architectures.

   Header Layout (14 Bytes):

    Byte Offset
    0x00 0x01 0x02 0x03 0x04 0x05 0x06 0x07 0x08 0x09 0x0A 0x0B 0x0C 0x0D
    +----+----+----+----+----+----+----+----+----+----+----+----+----+----+
    |  P |  S |  V |  I | Ver|Prec|       Vector Dimensions (uint32)      |
    +----+----+----+----+----+----+----+----+----+----+----+----+----+----+
    |  Dimensions (cont)  |          Compressed Payload Size (uint32)     |
    +----+----+----+----+----+----+----+----+----+----+----+----+----+----+
    
    Bytes 14+ : zlib Compressed Vector Payload (Variable Length)
    +...+...+...+...+...+...+...+...+...+...+...+...+...+...+...+...+...

   Field Definitions:

   - Magic Signature (Bytes 0-3, 4 bytes):
     MUST be the ASCII characters 'P', 'S', 'V', 'I' (0x50 0x53 0x56
     0x49). Nodes MUST reject any file lacking this signature.

   - Protocol Version (Byte 4, 1 byte):
     Unsigned 8-bit integer. Current specification is Version 1 (0x01).

   - Precision (Byte 5, 1 byte):
     Unsigned 8-bit integer defining the payload profile.
     0x00 = INT8 (Quantized with scale factor)
     0x01 = Float16 (Half precision)
     0x02 = Float32 (Single precision)

   - Vector Dimensions (Bytes 6-9, 4 bytes):
     Unsigned 32-bit integer (Little-Endian). Defines the number of
     elements in the vector (e.g., 4096 = 0x00 0x10 0x00 0x00).

   - Compressed Payload Size (Bytes 10-13, 4 bytes):
     Unsigned 32-bit integer (Little-Endian). The exact byte length of
     the zlib stream that follows the header.

4. Precision Profiles

   The payload, once decompressed via zlib (deflate/inflate), MUST
   conform strictly to the profile defined in the Precision byte.

4.1. Profile 0: INT8 (Maximum Compression)

   Used for dormant storage and edge devices. The uncompressed payload
   consists of a 4-byte float32 scale factor, followed by an array of
   signed 8-bit integers.

   Uncompressed Layout:
   [Scale Factor (4 bytes, float32)] [Vector Data (N bytes, int8)]

   Decompression Math:
   float32_value[i] = int8_value[i] * scale_factor

4.2. Profile 1: Float16 (Balanced)

   Used for sub-agent transit and critic corrections. The uncompressed
   payload is a raw array of IEEE 754 half-precision floats.

   Uncompressed Layout:
   [Vector Data (N * 2 bytes, float16)]

4.3. Profile 2: Float32 (Maximum Precision)

   Used for consensus deltas and master state generation. The
   uncompressed payload is a raw array of IEEE 754 single-precision
   floats.

   Uncompressed Layout:
   [Vector Data (N * 4 bytes, float32)]

5. Cryptographic Integrity and Sidecars

5.1. Content Addressing

   The filename of a .psvc container MUST be derived from the SHA-256
   hash of the *uncompressed, normalized float32 vector bytes*,
   truncated to 12 hexadecimal characters. This ensures that identical
   semantic concepts result in identical file hashes, enabling
   automatic deduplication across the Git-based memory bus.

5.2. Metadata Sidecars (FAIR Compliance)

   To satisfy FAIR (Findable, Accessible, Interoperable, Reusable)
   principles, every .psvc file SHOULD be accompanied by a JSON sidecar
   file sharing the same base name (e.g., a16330272f3f.json).

   The sidecar MUST contain:
   - text: The original semantic observation (if applicable).
   - agent: The name of the agent that generated the vector.
   - timestamp: ISO 8601 UTC timestamp of creation.
   - doi: (Optional) Zenodo DOI if the state has been published.

6. Security Considerations

   - Sandboxing: Volunteer nodes MUST NOT execute code embedded in the
     payload. The payload is strictly treated as a flat numeric array.
   - Memory Limits: The Mesh Governor enforces a "Pico Limit" (e.g., 5
     containers). Nodes MUST implement LRU (Least Recently Used)
     eviction to prevent VRAM exhaustion and Denial of Service (DoS).
   - Entropy Pruning: To prevent repository bloat, the Cortex agent
     periodically deletes raw containers that exhibit >95% cosine
     similarity to a Master State.

7. IANA Considerations

   - File Extension: .psvc
   - MIME Type: application/vnd.psivi.psvc+binary
   - Magic Number: 50 53 56 49 (ASCII "PSVI")

8. References

   [RFC2119]  Bradner, S., "Key words for use in RFCs to Indicate
              Requirement Levels", BCP 14, RFC 2119, March 1997.

   [FAIR]     Wilkinson, M. et al., "The FAIR Guiding Principles for
              scientific data management and stewardship", Scientific
              Data, 2016.

   [EUPL]     European Commission, "European Union Public Licence
              V. 1.2", 2016.

9. Author's Address

   Louis-Philippe Audette
   PSIVI Research
   Langford, BC, Canada
   Email: contact@psivi.com
   URI:   https://psivi.com
