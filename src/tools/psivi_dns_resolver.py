# tools/psivi_dns_resolver.py
# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2026 Louis-Philippe Audette | PSIVI.COM

"""
PSIVI-DNS Resolver
Client-side resolver that speaks the PSVC-DNS protocol.
Zero-copy query construction and response parsing.
"""

import socket
import time
import logging
from typing import Optional

import numpy as np

from tools.psivi_dns_envelope import (
    DNS_QUERY_DTYPE, DNS_RESPONSE_DTYPE, DNS_RECORD_DTYPE,
    hash_fqdn, pack_dns_query
)
from tools.psivi_mpk import PSIVIEncoder, PSIVIDecoder, MAGIC, HEADER_SIZE, CRC32_SIZE

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger("PSIVI_DNS_RESOLVER")


class PSIVIDNSResolver:
    """
    Client-side resolver for PSIVI-DNS.
    Constructs zero-copy queries and parses signed responses.
    """
    
    def __init__(self, server_host: str = "127.0.0.1", server_port: int = 5353, timeout: float = 2.0):
        self.server_host = server_host
        self.server_port = server_port
        self.timeout = timeout
        self.encoder = PSIVIEncoder(zstd_level=1)
        self.decoder = PSIVIDecoder()
        self.query_counter = 0

    def query(self, fqdn: str, record_type: int = 0x0001) -> Optional[np.ndarray]:
        """
        Sends a DNS query and returns the answer record (zero-copy view).
        
        Args:
            fqdn: Fully-qualified domain name (e.g., "hive.langford.psivi.com")
            record_type: DNS_TYPE_A, DNS_TYPE_PSVC, etc.
            
        Returns:
            numpy structured array view of the DNS_RECORD_DTYPE, or None if NXDOMAIN.
        """
        self.query_counter += 1
        query_id = self.query_counter
        name_hash = hash_fqdn(fqdn)
        
        # Construct the query (zero-copy)
        query = pack_dns_query(query_id, name_hash, record_type)
        query_envelope = self.encoder._build_envelope(query.tobytes())
        
        # Send via UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        
        try:
            sock.sendto(query_envelope, (self.server_host, self.server_port))
            response_envelope, _ = sock.recvfrom(4096)
            
            # Verify the response envelope
            if len(response_envelope) < HEADER_SIZE + CRC32_SIZE:
                logger.error("❌ Response envelope too small")
                return None
            if response_envelope[:4] != MAGIC:
                logger.error("❌ Invalid magic in response")
                return None
            
            # Decode the response (zero-copy)
            response_records = self.decoder.decode_to_view(response_envelope, dtype=DNS_RESPONSE_DTYPE)
            if len(response_records) == 0:
                return None
            
            response = response_records[0]
            status = int(response['status'])
            answer_count = int(response['answer_count'])
            
            if status != 0x00 or answer_count == 0:
                logger.info(f"ℹ️ NXDOMAIN for {fqdn}")
                return None
            
            # Return the answer record (zero-copy view)
            return response['answer']
            
        except socket.timeout:
            logger.error(f"❌ Query timeout for {fqdn}")
            return None
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            return None
        finally:
            sock.close()


def main():
    """Example usage: Resolve a PSVC envelope reference."""
    resolver = PSIVIDNSResolver(server_host="127.0.0.1", server_port=5353)
    
    fqdn = "hive.langford.psivi.com"
    logger.info(f"🔍 Resolving {fqdn}...")
    
    answer = resolver.query(fqdn, record_type=0x0001)  # DNS_TYPE_A
    
    if answer is not None:
        data_len = int(answer['data_len'])
        data = answer['data'][:data_len].tobytes()
        logger.info(f"✅ Answer: {data}")
    else:
        logger.info("❌ No answer")


if __name__ == "__main__":
    main()
