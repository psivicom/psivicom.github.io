# src/utils/oidc_verifier.py
import os
import json
import time
import base64
import requests
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

def get_github_public_keys():
    """Fetches the current public keys from GitHub's OIDC endpoint."""
    url = "https://api.github.com/meta/public-keys/token_signing"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['public_keys']

def decode_jwt_part(part):
    """Decodes a base64url encoded JWT part with proper padding."""
    part += '=' * (4 - len(part) % 4)
    return json.loads(base64.urlsafe_b64decode(part))

def verify_oidc_token(token: str, audience: str = "psivi.com") -> bool:
    try:
        header, payload, signature = token.split('.')
        
        # 1. Decode Payload to check Expiration and Audience
        payload_data = decode_jwt_part(payload)
        
        # Check Expiration
        if payload_data['exp'] < time.time():
            print("❌ Token has expired.")
            return False

        # Check Audience (Handle both String and Array formats)
        token_aud = payload_data.get('aud')
        if isinstance(token_aud, str):
            token_aud = [token_aud]
            
        if audience not in token_aud:
            print(f"❌ Invalid audience. Expected: {audience}, Got: {token_aud}")
            return False

        # 2. Verify Signature against GitHub Public Keys
        keys = get_github_public_keys()
        header_data = decode_jwt_part(header)
        key_id = header_data.get('kid')
        
        signing_key = None
        for key in keys:
            if key['key_identifier'] == key_id:
                signing_key = key['key']
                break
        
        if not signing_key:
            print("❌ No matching public key found for this token.")
            return False

        # Convert PEM key to cryptography object
        public_key = serialization.load_pem_public_key(
            signing_key.encode(),
            backend=default_backend()
        )

        # Verify the signature
        message = f"{header}.{payload}".encode()
        sig = base64.urlsafe_b64decode(signature + '=' * (4 - len(signature) % 4))
        
        public_key.verify(
            sig,
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        print("✅ OIDC Token verified successfully.")
        return True

    except Exception as e:
        print(f"❌ OIDC Verification failed: {e}")
        return False
