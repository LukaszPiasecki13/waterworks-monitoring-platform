"""Tests for EC signature verification."""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from app.modules.device_identity.services.signature import verify_signature


def test_verify_signature_valid():
    """Test signature verification with valid signature."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )

    message = b"test message"
    signature_der = private_key.sign(message, ec.ECDSA(hashes.SHA256()))

    assert verify_signature(public_key_pem, message, signature_der) is True


def test_verify_signature_invalid():
    """Test signature verification with invalid signature."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )

    message = b"test message"
    wrong_signature = b"invalid_signature"

    assert verify_signature(public_key_pem, message, wrong_signature) is False


def test_verify_signature_wrong_message():
    """Test signature verification with wrong message."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode()
    )

    message = b"test message"
    signature_der = private_key.sign(message, ec.ECDSA(hashes.SHA256()))

    assert (
        verify_signature(public_key_pem, b"different message", signature_der) is False
    )
