# tools/psivi_dns_server.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
PSIVI-DNS Server
A sovereign, zero-copy DNS server that resolves names to PSVC envelopes.
Uses Bloom filters for O(1) lookups and cryptographic signatures for provenance.
"""

import socket
import struct
import logging
import mmap
import os
from pathlib import Path
from typing import Optional, Dict

import numpy as np
import yaml

from tools.psivi_dns_envelope import (
    DNS_RECORD_DTYPE, DNS_QUERY_DTYPE, DNS_RESPONSE_DTYPE,
    hash_fqdn, pack_dns_response, DNS_TYPE_A, DNS_TYPE_PSVC
)
from tools.psivi_mpk import PSIVIEncoder, PSIVIDecoder, MeshBloomFilter, MAGIC, HEADER_SIZE, CRC32_SIZE

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("PSIVI_DNS_SERVER")


class PSIVIDNSServer:
    """
    Sovereign DNS server.
    Loads zone files as memory-mapped PSVC envelopes.
    Uses Bloom filters for O(1) "do I have this name?" checks.
    """
    
    def __init__(self, config_path: str = "config/psivi_dns.yaml"):
        self.config = self._load_config(config_path)
        self.encoder = PSIVIEncoder(zstd_level=1)
        self.decoder = PSIVIDecoder()
        
        # Zone storage: name_hash -> DNS_RECORD_DTYPE
        self.zone: Dict[int, np.ndarray] = {}
        
        # Bloom filter for O(1) existence checks
        self.bloom = MeshBloomFilter(size_bytes=65536)
        
        # Load zone files
        self._load_zone_files()
        
        logger.info(f"🌐 PSIVI-DNS Server initialized. Zone size: {len(self.zone)} records.")

    def _load_config(self, config_path: str) -> dict:
        """Loads server configuration from YAML."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config not found: {config_path}. Using defaults.")
            return {
                "server": {"bind": "0.0.0.0", "port": 5353},
                "zone_dir": "data/dns_zones",
                "upstream": None
            }

    def _load_zone_files(self):
        """
        Loads zone files from the zone directory.
        Zone files are PSVC envelopes containing arrays of DNS_RECORD_DTYPE.
        """
        zone_dir = Path(self.config.get("zone_dir", "data/dns_zones"))
        zone_dir.mkdir(parents=True, exist_ok=True)
        
        for zone_file in zone_dir.glob("*.psvc"):
            try:
                envelope_bytes = zone_file.read_bytes()
                records = self.decoder.decode_to_view(envelope_bytes, dtype=DNS_RECORD_DTYPE)
                
                for record in records:
                    name_hash = int(record['name_hash'])
                    self.zone[name_hash] = record
                    self.bloom.add(name_hash.to_bytes(8, 'little'))
                
                logger.info(f"✅ Loaded zone: {zone_file.name} ({len(records)} records)")
            except Exception as e:
                logger.error(f"❌ Failed to load zone {zone_file.name}: {e}")

    def resolve(self, query_bytes: bytes) -> Optional[bytes]:
        """
        Resolves a DNS query.
        Input: Raw PSVC envelope containing a DNS_QUERY_DTYPE.
        Output: Raw PSVC envelope containing a DNS_RESPONSE_DTYPE.
        """
        try:
            # Decode the query envelope (zero-copy)
            query_records = self.decoder.decode_to_view(query_bytes, dtype=DNS_QUERY_DTYPE)
            if len(query_records) == 0:
                return None
            
            query = query_records[0]
            query_id = int(query['query_id'])
            name_hash = int(query['name_hash'])
            record_type = int(query['record_type'])
            
            # O(1) Bloom filter check
            name_bytes = name_hash.to_bytes(8, 'little')
            if not self.bloom.check(name_bytes):
                # Name not in zone
                response = pack_dns_response(query_id, 0x03, 0, query, np.zeros(1, dtype=DNS_RECORD_DTYPE))
                return self.encoder._build_envelope(response.tobytes())
            
            # Lookup in zone
            if name_hash in self.zone:
                answer = self.zone[name_hash]
                if int(answer['record_type']) == record_type:
                    response = pack_dns_response(query_id, 0x00, 1, query, answer)
                    return self.encoder._build_envelope(response.tobytes())
            
            # Name exists but wrong record type
            response = pack_dns_response(query_id, 0x03, 0, query, np.zeros(1, dtype=DNS_RECORD_DTYPE))
            return self.encoder._build_envelope(response.tobytes())
            
        except Exception as e:
            logger.error(f"❌ Resolution failed: {e}")
            return None

    def serve(self):
        """
        Starts the UDP server loop.
        Listens for PSVC-DNS queries and responds with signed envelopes.
        """
        bind = self.config.get("server", {}).get("bind", "0.0.0.0")
        port = self.config.get("server", {}).get("port", 5353)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((bind, port))
        
        logger.info(f"🚀 PSIVI-DNS Server listening on {bind}:{port}")
        
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                
                # Verify the envelope is a valid PSVC
                if len(data) < HEADER_SIZE + CRC32_SIZE:
                    continue
                if data[:4] != MAGIC:
                    continue
                
                # Resolve the query
                response_bytes = self.resolve(data)
                
                if response_bytes:
                    sock.sendto(response_bytes, addr)
                    
            except KeyboardInterrupt:
                logger.info("🛑 Server shutting down.")
                break
            except Exception as e:
                logger.error(f"❌ Server error: {e}")


def main():
    server = PSIVIDNSServer()
    server.serve()


if __name__ == "__main__":
    main()
