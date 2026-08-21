"""Shared fixtures for device_identity tests."""

from uuid import uuid4

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


@pytest.fixture
def ec_key_pair():
    """Generate a P-256 EC key pair for testing."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    return {
        "private_key": private_key,
        "public_key": public_key,
        "private_pem": private_pem,
        "public_pem": public_pem,
    }


@pytest.fixture
def test_serial_number():
    """Generate a test serial number."""
    return f"TEST-SN-{uuid4().hex[:8].upper()}"


@pytest.fixture
def test_device_id():
    """Generate a test device ID."""
    return uuid4()


@pytest.fixture
def test_credential_id():
    """Generate a test credential ID."""
    return uuid4()


@pytest.fixture
def test_water_object_id():
    """Generate a test water object ID."""
    return uuid4()
