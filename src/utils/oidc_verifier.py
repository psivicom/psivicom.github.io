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
    """Decodes a base64url encoded JWT part."""
    part += '=' * (4 - len(part) % 4)  # Add padding
    return json.loads(base64.urlsafe_b64decode(part))

def verify_oidc_token(token: str, audience: str = "psivi.com") -> bool:
    """
    Verifies a GitHub OIDC token.
    
    Args:
        token: The JWT string from ${{ steps.get-token.outputs.result }}
        audience: The expected audience (e.g., 'psivi.com')
        
    Returns:
        True if the token is valid and signed by GitHub.
    """
    try:
        header, payload, signature = token.split('.')
        
        # 1. Check Expiration
        if payload['exp'] < time.time():
            print("❌ Token has expired.")
            return False

        # 2. Check Audience
        if audience not in payload.get('aud', []):
            print(f"❌ Invalid audience. Expected: {audience}")
            return False

        # 3. Verify Signature against GitHub Public Keys
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

if __name__ == "__main__":
    oidc_token = os.environ.get('OIDC_TOKEN')
    if oidc_token:
        verify_oidc_token(oidc_token)
    else:
        print("⚠️ No OIDC_TOKEN found in environment.")