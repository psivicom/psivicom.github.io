#!/usr/bin/env python3
"""
/gemini_client.py — Pure Socket Gemini Protocol Fetcher
Connects to port 1965 via TLS to fetch .gmi capsules without HTTP bloat.
"""
import ssl
import socket
import urllib.parse

class GeminiClient:
    @staticmethod
    def fetch(url: str) -> str:
        """Fetches raw Gemtext from a Gemini server."""
        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname
        port = parsed.port or 1965
        
        # Gemini relies on strict TLS, but often uses self-signed certs for local loops
        context = ssl.create_default_context()
        context.check_hostname = False 
        context.verify_mode = ssl.CERT_NONE
        
        try:
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    # Gemini request format is strictly the URL followed by CRLF
                    ssock.sendall(f"{url}\r\n".encode("UTF-8"))
                    
                    response = b""
                    while True:
                        chunk = ssock.recv(4096)
                        if not chunk: 
                            break
                        response += chunk
                        
            decoded = response.decode("UTF-8")
            header, body = decoded.split("\r\n", 1)
            status = header[:2]
            
            if status == "20":
                return body
            else:
                raise Exception(f"Gemini server returned status {status}: {header}")
                
        except Exception as e:
            raise Exception(f"Failed to fetch {url}: {str(e)}")

if __name__ == "__main__":
    # Local test
    print(GeminiClient.fetch("gemini://gemini.circumlunar.space/"))
