"""Unit tests for DeviceService — detach_from_organization and delete_device_record."""

from functools import partial
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from app.core.errors import NotFoundError
from app.infrastructure.sql.repository import SQLRepository
from app.modules.core_data.services.devices import DeviceService
from app.modules.security.access import OrganizationAccess


@pytest.fixture
def mock_repo() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_water_object_repo() -> MagicMock:
    return MagicMock()


@pytest.fixture
def mock_audit() -> MagicMock:
    return MagicMock()


@pytest.fixture
def service(
    mock_repo: MagicMock, mock_water_object_repo: MagicMock, mock_audit: MagicMock
) -> DeviceService:
    service = DeviceService.__new__(DeviceService)
    service.repo = mock_repo
    service.water_object_repo = mock_water_object_repo
    service.audit = mock_audit
    mock_repo.flush = MagicMock()
    mock_repo.refresh = MagicMock()
    mock_repo.commit = MagicMock()
    mock_repo.rollback = MagicMock()
    mock_repo.transaction = partial(SQLRepository.transaction, mock_repo)
    return service


def mock_device(
    device_id: UUID | None = None,
    external_id: str = "WW-TEST123",
    water_object_id: UUID | None = None,
    credential_id: UUID | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=device_id or uuid4(),
        external_id=external_id,
        water_object_id=water_object_id,
        device_credential_id=credential_id or uuid4(),
        firmware_version="1.0.0",
        is_active=True,
    )


def test_detach_from_organization_sets_water_object_id_to_none(
    service: DeviceService,
    mock_repo: MagicMock,
    mock_audit: MagicMock,
) -> None:
    """detach_from_organization should set water_object_id to None."""
    device_id = uuid4()
    org_id = uuid4()
    water_object_id = uuid4()
    device = mock_device(device_id=device_id, water_object_id=water_object_id)

    mock_repo.find_in_organization.return_value = device
    mock_repo.assign_water_object.return_value = None

    actor = SimpleNamespace(id=uuid4(), email="user@example.com")
    org_access = OrganizationAccess(
        actor=actor,
        organization_id=org_id,
        permissions=set(),
    )

    service.detach_from_organization(device_id, org_access)

    mock_repo.find_in_organization.assert_called_once_with(device_id, org_id)
    mock_repo.assign_water_object.assert_called_once_with(device, None)
    mock_repo.flush.assert_called_once()
    mock_repo.refresh.assert_called_once_with(device)
    assert mock_audit.record.called


def test_detach_from_organization_raises_not_found_if_device_not_in_org(
    service: DeviceService,
    mock_repo: MagicMock,
) -> None:
    """detach_from_organization should raise NotFoundError if device not in org."""
    device_id = uuid4()
    org_id = uuid4()

    mock_repo.find_in_organization.side_effect = NotFoundError("Device not found")

    actor = SimpleNamespace(id=uuid4(), email="user@example.com")
    org_access = OrganizationAccess(
        actor=actor,
        organization_id=org_id,
        permissions=set(),
    )

    with pytest.raises(NotFoundError):
        service.detach_from_organization(device_id, org_access)


def test_delete_device_record_deletes_and_audits(
    service: DeviceService,
    mock_repo: MagicMock,
    mock_audit: MagicMock,
) -> None:
    """delete_device_record should delete device and record audit."""
    device_id = uuid4()
    device = mock_device(device_id=device_id)

    mock_repo.find_by_id.return_value = device
    mock_repo.delete.return_value = None

    actor_id = str(uuid4())
    actor_display_name = "admin@example.com"

    result = service.delete_device_record(device_id, actor_id, actor_display_name)

    mock_repo.find_by_id.assert_called_once_with(device_id)
    mock_repo.delete.assert_called_once_with(device)
    assert mock_audit.record.called
    assert result == device


def test_delete_device_record_raises_not_found_if_missing(
    service: DeviceService,
    mock_repo: MagicMock,
) -> None:
    """delete_device_record should raise NotFoundError if device missing."""
    device_id = uuid4()

    mock_repo.find_by_id.side_effect = NotFoundError("Device not found")

    with pytest.raises(NotFoundError):
        service.delete_device_record(device_id, "actor-id", "actor@example.com")
