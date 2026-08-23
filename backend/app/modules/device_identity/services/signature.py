"""EC signature verification and key conversion for device claims."""

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_public_key,
)

from app.core.errors import BadRequestError


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


def public_key_point_hex_to_pem(point_hex: str) -> str:
    """Convert an uncompressed EC P-256 point (hex) to PEM format.

    Args:
        point_hex: Uncompressed P-256 point as hex string (130 chars: 04 + X + Y)

    Returns:
        PEM-encoded EC public key (SPKI format)

    Raises:
        BadRequestError: If point format is invalid
    """
    try:
        point_bytes = bytes.fromhex(point_hex)
    except ValueError as err:
        raise BadRequestError("Invalid public key point encoding") from err

    if len(point_bytes) != 65 or point_bytes[0] != 0x04:
        raise BadRequestError(
            "Invalid public key point: expected uncompressed P-256 point"
        )

    try:
        public_key = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256R1(), point_bytes
        )
    except ValueError as err:
        raise BadRequestError("Public key point is not on curve P-256") from err

    return public_key.public_bytes(
        Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
    ).decode()
