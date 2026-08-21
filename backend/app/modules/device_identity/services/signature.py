"""EC signature verification for device claims."""

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_public_key


def verify_signature(public_key_pem: str, message: bytes, signature_der: bytes) -> bool:
    """Verify an ECDSA P-256 signature over a message.

    Args:
        public_key_pem: PEM-encoded EC public key
        message: Message bytes that were signed
        signature_der: DER-encoded signature

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        public_key = load_pem_public_key(public_key_pem.encode())
        public_key.verify(signature_der, message, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False
    except ValueError, TypeError, AttributeError:
        return False
