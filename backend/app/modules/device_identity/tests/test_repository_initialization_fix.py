"""Test for repository initialization fix.

This test verifies the fix for:
TypeError: SQLRepository.__init__() takes 2 positional arguments but 3 were given

The bug was in DeviceCredentialRepository.__init__ calling:
    super().__init__(session, DeviceCredential)  # Wrong: 2 arguments
Instead of:
    super().__init__(session)  # Correct: 1 argument
"""

from app.modules.device_identity.repositories.device_credentials import (
    DeviceCredentialRepository,
)


def test_device_credential_repository_can_be_instantiated(db_session):
    """Test repository instantiation works without TypeError.

    Before the fix, this would fail with:
    TypeError: SQLRepository.__init__() takes 2 positional arguments but 3 were given
    """
    # This is the critical test - it demonstrates the fix
    repo = DeviceCredentialRepository(db_session)

    # Verify the repository is properly initialized
    assert repo is not None
    assert repo.session == db_session


def test_repository_via_dependency_injection(db_session):
    """Test repository can be created via dependency injection."""
    from app.modules.device_identity.dependencies import (
        get_credential_repo,
    )

    # This simulates what happens in the FastAPI endpoint
    # when the dependency injection system tries to instantiate the repository
    repo = get_credential_repo(db_session)

    assert repo is not None
    assert isinstance(repo, DeviceCredentialRepository)
