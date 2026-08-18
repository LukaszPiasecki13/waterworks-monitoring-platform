"""
Seed script to populate the database with test data.
Usage: python scripts/seed_database.py
"""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

# Add the backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.infrastructure.sql.factory import SQLConnectionFactory
from app.modules.core_data.models.device import Device
from app.modules.core_data.models.measurement_point import MeasurementPoint
from app.modules.core_data.models.organization import Organization
from app.modules.core_data.models.user import User
from app.modules.core_data.models.users_organizations import UsersOrganizations
from app.modules.core_data.models.water_object import WaterObject
from app.modules.security.models import Permission, UserGroup
from app.modules.security.permission_catalog import (
    ADMIN_GROUP_KEY,
    PERMISSION_CATALOG,
    STAFF_GROUP_KEY,
    VIEW_PERMISSIONS,
)
from app.modules.security.services.password import hash_password
from app.modules.telemetry.models.measurement_packet import TelemetryPacket


def _cleanup_duplicates(session: Session) -> None:
    """Remove duplicate water objects and old telemetry data."""
    from app.modules.core_data.models.device import Device
    from app.modules.core_data.models.measurement_point import MeasurementPoint
    from app.modules.telemetry.models.measurement_packet import TelemetryPacket

    print("\n🧹 Cleaning up database...")

    # Get all water objects grouped by name
    all_objects = session.query(WaterObject).all()
    seen_names = {}
    to_delete = []

    for obj in all_objects:
        if obj.name not in seen_names:
            seen_names[obj.name] = obj.id
        else:
            to_delete.append(obj.id)

    deleted_water_objects = 0

    if to_delete:
        # Delete telemetry packets for devices in duplicate objects
        devices_to_delete = (
            session.query(Device).filter(Device.water_object_id.in_(to_delete)).all()
        )
        device_ids = [str(d.id) for d in devices_to_delete]

        if device_ids:
            session.query(TelemetryPacket).filter(
                TelemetryPacket.device_id.in_(device_ids)
            ).delete()

        # Delete measurement points for duplicate devices
        session.query(MeasurementPoint).filter(
            MeasurementPoint.device_id.in_(device_ids)
        ).delete()

        # Delete duplicate devices
        session.query(Device).filter(Device.water_object_id.in_(to_delete)).delete()

        # Delete duplicate water objects
        deleted_water_objects = (
            session.query(WaterObject).filter(WaterObject.id.in_(to_delete)).delete()
        )

    # Also clear all old telemetry packets to start fresh
    deleted_all_packets = session.query(TelemetryPacket).delete()

    session.commit()

    if deleted_water_objects > 0:
        print(f"  ✓ Deleted {deleted_water_objects} duplicate water objects")
    if deleted_all_packets > 0:
        print(f"  ✓ Cleared {deleted_all_packets} telemetry packets")
    if deleted_water_objects == 0 and deleted_all_packets == 0:
        print("  ✓ No cleanup needed")


def _seed_security(session: Session) -> tuple[int, int, UserGroup, UserGroup]:
    """Seed security permissions and groups.

    Returns (permissions_count, groups_count, admin_group, staff_group).
    """
    # Create permissions from catalog
    permissions_created = 0
    for perm_def in PERMISSION_CATALOG:
        existing = session.query(Permission).filter_by(code=perm_def.code).first()
        if not existing:
            perm = Permission(
                code=perm_def.code,
                name=perm_def.name,
                category=perm_def.category,
            )
            session.add(perm)
            permissions_created += 1

    session.flush()
    session.commit()

    # Get all permissions for admin group
    all_permissions = session.query(Permission).all()

    # Create admin group
    admin_group = session.query(UserGroup).filter_by(system_key=ADMIN_GROUP_KEY).first()
    if not admin_group:
        admin_group = UserGroup(
            name="Admin",
            description="Full system access",
            is_system=True,
            system_key=ADMIN_GROUP_KEY,
            permissions=all_permissions,
        )
        session.add(admin_group)
        session.flush()

    # Create staff group
    staff_group = session.query(UserGroup).filter_by(system_key=STAFF_GROUP_KEY).first()
    if not staff_group:
        view_permissions = (
            session.query(Permission)
            .filter(Permission.code.in_(VIEW_PERMISSIONS))
            .all()
        )
        staff_group = UserGroup(
            name="Staff",
            description="Read-only access",
            is_system=True,
            system_key=STAFF_GROUP_KEY,
            permissions=view_permissions,
        )
        session.add(staff_group)
        session.flush()

    groups_created = 2  # Admin + Staff
    return permissions_created, groups_created, admin_group, staff_group


def seed_database():
    """Populate database with realistic test data."""

    settings = get_settings()
    sql_factory = SQLConnectionFactory()
    engine = sql_factory.get_or_create_engine(
        settings.database_url, settings.database_schema
    )

    with Session(engine) as session:
        print("🌱 Starting database seeding...")

        # Clean up duplicates first
        _cleanup_duplicates(session)

        # 0. Seed Security (Permissions & Groups)
        print("\n🔐 Seeding security permissions and groups...")
        perms_count, groups_count, admin_group, staff_group = _seed_security(session)
        session.commit()
        print(f"  ✓ Created {perms_count} permissions and {groups_count} groups")

        # 1. Create Organizations
        print("\n📦 Creating organizations...")
        org1 = session.query(Organization).filter_by(name="Gmina Frysztak").first()
        if not org1:
            org1 = Organization(id=uuid4(), name="Gmina Frysztak")
            session.add(org1)

        org2 = session.query(Organization).filter_by(name="Gmina Radziłów").first()
        if not org2:
            org2 = Organization(id=uuid4(), name="Gmina Radziłów")
            session.add(org2)

        session.commit()
        print("  ✓ Created 2 organizations")

        # 2. Create Users
        print("\n👥 Creating users...")

        # Global admin (can see all organizations)
        admin_global = session.query(User).filter_by(username="admin").first()
        if not admin_global:
            admin_global = User(
                id=uuid4(),
                username="admin",
                email="admin@waterworks.local",
                first_name="Adam",
                last_name="Administrator",
                hashed_password=hash_password("password123"),
                is_active=True,
            )
            session.add(admin_global)

        # Gmina Frysztak - viewer
        viewer_frysztak = (
            session.query(User).filter_by(username="viewer_frysztak").first()
        )
        if not viewer_frysztak:
            viewer_frysztak = User(
                id=uuid4(),
                username="viewer_frysztak",
                email="viewer@gmina-frysztak.pl",
                first_name="Stanisław",
                last_name="Obserwator",
                hashed_password=hash_password("password123"),
                is_active=True,
            )
            session.add(viewer_frysztak)

        # Gmina Radziłów - viewer
        viewer_radzilow = (
            session.query(User).filter_by(username="viewer_radzilow").first()
        )
        if not viewer_radzilow:
            viewer_radzilow = User(
                id=uuid4(),
                username="viewer_radzilow",
                email="viewer@gmina-radzilow.pl",
                first_name="Stefan",
                last_name="Obserwator",
                hashed_password=hash_password("password123"),
                is_active=True,
            )
            session.add(viewer_radzilow)

        session.flush()

        # Add users to organizations (M:N relationship)
        # Admin belongs to both organizations
        org1_admin = (
            session.query(UsersOrganizations)
            .filter_by(user_id=admin_global.id, organization_id=org1.id)
            .first()
        )
        if not org1_admin:
            session.add(
                UsersOrganizations(user_id=admin_global.id, organization_id=org1.id)
            )

        org2_admin = (
            session.query(UsersOrganizations)
            .filter_by(user_id=admin_global.id, organization_id=org2.id)
            .first()
        )
        if not org2_admin:
            session.add(
                UsersOrganizations(user_id=admin_global.id, organization_id=org2.id)
            )

        # Viewer Frysztak belongs to org1
        org1_viewer = (
            session.query(UsersOrganizations)
            .filter_by(user_id=viewer_frysztak.id, organization_id=org1.id)
            .first()
        )
        if not org1_viewer:
            session.add(
                UsersOrganizations(user_id=viewer_frysztak.id, organization_id=org1.id)
            )

        # Viewer Radzilow belongs to org2
        org2_viewer = (
            session.query(UsersOrganizations)
            .filter_by(user_id=viewer_radzilow.id, organization_id=org2.id)
            .first()
        )
        if not org2_viewer:
            session.add(
                UsersOrganizations(user_id=viewer_radzilow.id, organization_id=org2.id)
            )

        session.commit()
        print("  ✓ Created users and assigned to organizations")

        # 3. Create Water Objects
        print("\n💧 Creating water objects...")

        # Gmina Frysztak
        fr_intake = (
            session.query(WaterObject)
            .filter_by(name="Ujęcie wody - Jezioro Frysztak")
            .first()
        )
        if not fr_intake:
            fr_intake = WaterObject(
                id=uuid4(),
                organization_id=org1.id,
                name="Ujęcie wody - Jezioro Frysztak",
                object_type="intake",
                location_description=(
                    "Główne ujęcie wody powierzchniowej z jeziora Frysztak"
                ),
                latitude=50.1625,
                longitude=21.2483,
                is_active=True,
            )
            session.add(fr_intake)

        fr_treatment = (
            session.query(WaterObject)
            .filter_by(name="Stacja uzdatniania wody Frysztak")
            .first()
        )
        if not fr_treatment:
            fr_treatment = WaterObject(
                id=uuid4(),
                organization_id=org1.id,
                name="Stacja uzdatniania wody Frysztak",
                object_type="water_treatment",
                location_description=(
                    "Główna stacja uzdatniania wody, ul. Wodna 5, Frysztak"
                ),
                latitude=50.1630,
                longitude=21.2490,
                is_active=True,
            )
            session.add(fr_treatment)

        # Gmina Radziłów
        rad_intake = (
            session.query(WaterObject)
            .filter_by(name="Ujęcie wody - Rzeka Narew")
            .first()
        )
        if not rad_intake:
            rad_intake = WaterObject(
                id=uuid4(),
                organization_id=org2.id,
                name="Ujęcie wody - Rzeka Narew",
                object_type="intake",
                location_description="Ujęcie wody z rzeki Narew w Radziłowie",
                latitude=52.9167,
                longitude=22.6833,
                is_active=True,
            )
            session.add(rad_intake)

        rad_treatment = (
            session.query(WaterObject)
            .filter_by(name="Stacja uzdatniania wody Radziłów")
            .first()
        )
        if not rad_treatment:
            rad_treatment = WaterObject(
                id=uuid4(),
                organization_id=org2.id,
                name="Stacja uzdatniania wody Radziłów",
                object_type="water_treatment",
                location_description=(
                    "Stacja uzdatniania wody, ul. Słoneczna 12, Radziłów"
                ),
                latitude=52.9170,
                longitude=22.6840,
                is_active=True,
            )
            session.add(rad_treatment)

        session.commit()
        print("  ✓ Created water objects (checked for existing)")

        # 4. Create Devices
        print("\n📱 Creating devices...")

        # Gmina Frysztak devices
        # ESP32 device for telemetry
        dev_esp32 = (
            session.query(Device).filter_by(external_id="esp32-a7670e-0001").first()
        )
        if not dev_esp32:
            dev_esp32 = Device(
                id=uuid4(),
                water_object_id=fr_intake.id,
                external_id="esp32-a7670e-0001",
                hashed_secret=hash_password("Test1"),
                firmware_version="1.0.0",
                last_seen_at=datetime.now(UTC),
                is_active=True,
            )
            session.add(dev_esp32)

        dev_fr_intake = (
            session.query(Device).filter_by(external_id="FR-INTAKE-001").first()
        )
        if not dev_fr_intake:
            dev_fr_intake = Device(
                id=uuid4(),
                water_object_id=fr_intake.id,
                external_id="FR-INTAKE-001",
                hashed_secret=hash_password("device_secret_123"),
                firmware_version="2.1.5",
                last_seen_at=datetime.now(UTC),
                is_active=True,
            )
            session.add(dev_fr_intake)

        dev_fr_treatment = (
            session.query(Device).filter_by(external_id="FR-TREATMENT-001").first()
        )
        if not dev_fr_treatment:
            dev_fr_treatment = Device(
                id=uuid4(),
                water_object_id=fr_treatment.id,
                external_id="FR-TREATMENT-001",
                hashed_secret=hash_password("device_secret_456"),
                firmware_version="2.0.3",
                last_seen_at=datetime.now(UTC),
                is_active=True,
            )
            session.add(dev_fr_treatment)

        # Gmina Radziłów devices
        dev_rad_intake = (
            session.query(Device).filter_by(external_id="RAD-INTAKE-001").first()
        )
        if not dev_rad_intake:
            dev_rad_intake = Device(
                id=uuid4(),
                water_object_id=rad_intake.id,
                external_id="RAD-INTAKE-001",
                hashed_secret=hash_password("device_secret_789"),
                firmware_version="2.2.0",
                last_seen_at=datetime.now(UTC),
                is_active=True,
            )
            session.add(dev_rad_intake)

        dev_rad_treatment = (
            session.query(Device).filter_by(external_id="RAD-TREATMENT-001").first()
        )
        if not dev_rad_treatment:
            dev_rad_treatment = Device(
                id=uuid4(),
                water_object_id=rad_treatment.id,
                external_id="RAD-TREATMENT-001",
                hashed_secret=hash_password("device_secret_012"),
                firmware_version="1.9.8",
                last_seen_at=datetime.now(UTC),
                is_active=True,
            )
            session.add(dev_rad_treatment)

        session.commit()
        print("  ✓ Created devices (checked for existing)")

        # 5. Create Measurement Points
        print("\n📊 Creating measurement points...")

        measurement_points_config = [
            (dev_fr_intake.id, "FR-INTAKE-001-FLOW", "flow_rate", "m³/h", 0.0, 300.0),
            (dev_fr_intake.id, "FR-INTAKE-001-TEMP", "temperature", "°C", 2.0, 28.0),
            (
                dev_fr_treatment.id,
                "FR-TREATMENT-001-FLOW",
                "flow_rate",
                "m³/h",
                0.0,
                300.0,
            ),
            (
                dev_fr_treatment.id,
                "FR-TREATMENT-001-TURBIDITY",
                "turbidity",
                "NTU",
                0.0,
                5.0,
            ),
            (dev_rad_intake.id, "RAD-INTAKE-001-FLOW", "flow_rate", "m³/h", 0.0, 350.0),
            (dev_rad_intake.id, "RAD-INTAKE-001-TEMP", "temperature", "°C", 1.0, 30.0),
            (
                dev_rad_treatment.id,
                "RAD-TREATMENT-001-FLOW",
                "flow_rate",
                "m³/h",
                0.0,
                350.0,
            ),
            (
                dev_rad_treatment.id,
                "RAD-TREATMENT-001-TURBIDITY",
                "turbidity",
                "NTU",
                0.0,
                5.0,
            ),
        ]

        for (
            device_id,
            ext_id,
            point_type,
            unit,
            min_val,
            max_val,
        ) in measurement_points_config:
            existing = (
                session.query(MeasurementPoint)
                .filter_by(device_id=device_id, external_id=ext_id)
                .first()
            )
            if not existing:
                mp = MeasurementPoint(
                    id=uuid4(),
                    device_id=device_id,
                    external_id=ext_id,
                    point_type=point_type,
                    unit=unit,
                    min_technical=min_val,
                    max_technical=max_val,
                    is_active=True,
                )
                session.add(mp)

        session.commit()
        print("  ✓ Created measurement points (checked for existing)")

        # 6. Generate Telemetry Packets
        print("\n📡 Generating telemetry packets...")

        now = datetime.now(UTC)
        packets_created = 0

        # Map measurement point external_ids to database IDs and their types/units
        measurement_point_map = {}
        mps = session.query(MeasurementPoint).all()
        for mp in mps:
            measurement_point_map[mp.external_id] = {
                "id": str(mp.id),
                "type": mp.point_type,
                "unit": mp.unit,
            }

        # Generate realistic telemetry data for the past 7 days
        devices = [
            (
                dev_fr_intake,
                org1.id,
                fr_intake.id,
                [
                    (
                        "FR-INTAKE-001-FLOW",
                        lambda i: 180 + 60 * ((now.hour + i) % 24) / 24,
                    ),
                    (
                        "FR-INTAKE-001-TEMP",
                        lambda i: 12 + 8 * ((now.hour + i) % 24) / 24,
                    ),
                ],
            ),
            (
                dev_fr_treatment,
                org1.id,
                fr_treatment.id,
                [
                    (
                        "FR-TREATMENT-001-FLOW",
                        lambda i: 175 + 60 * ((now.hour + i) % 24) / 24,
                    ),
                    (
                        "FR-TREATMENT-001-TURBIDITY",
                        lambda i: 0.3 + 0.2 * ((now.hour + i) % 24) / 24,
                    ),
                ],
            ),
            (
                dev_rad_intake,
                org2.id,
                rad_intake.id,
                [
                    (
                        "RAD-INTAKE-001-FLOW",
                        lambda i: 200 + 70 * ((now.hour + i) % 24) / 24,
                    ),
                    (
                        "RAD-INTAKE-001-TEMP",
                        lambda i: 10 + 12 * ((now.hour + i) % 24) / 24,
                    ),
                ],
            ),
            (
                dev_rad_treatment,
                org2.id,
                rad_treatment.id,
                [
                    (
                        "RAD-TREATMENT-001-FLOW",
                        lambda i: 195 + 70 * ((now.hour + i) % 24) / 24,
                    ),
                    (
                        "RAD-TREATMENT-001-TURBIDITY",
                        lambda i: 0.4 + 0.25 * ((now.hour + i) % 24) / 24,
                    ),
                ],
            ),
        ]

        for device, _org_id, _obj_id, measurements in devices:
            # Generate 100 packets per device over the past 7 days
            for i in range(100):
                timestamp = now - timedelta(hours=i)

                # Build points array with correct structure
                points = []
                for mpoint_id, measurement_func in measurements:
                    if mpoint_id in measurement_point_map:
                        mp_info = measurement_point_map[mpoint_id]
                        points.append(
                            {
                                "point_id": mp_info["id"],
                                "type": mp_info["type"],
                                "unit": mp_info["unit"],
                                "value": measurement_func(i),
                                "quality": "good" if i % 10 != 0 else "warning",
                            }
                        )

                # Create payload with windows format (expected by TelemetryQueryService)
                packet = TelemetryPacket(
                    id=uuid4(),
                    device_id=str(device.external_id),
                    seq=i + 1,
                    sent_at=timestamp,
                    received_at=timestamp + timedelta(seconds=2),
                    payload={
                        "windows": [
                            {
                                "window_start": timestamp.isoformat(),
                                "points": points,
                            }
                        ],
                        "device_info": {
                            "battery": 85 - (i % 50),
                            "signal_strength": -60 - (i % 30),
                            "uptime_seconds": 864000 - (i * 3600),
                        },
                    },
                )
                session.add(packet)
                packets_created += 1

            session.commit()

        print(f"  ✓ Created {packets_created} telemetry packets")

        # Assign users to groups
        print("\n👥 Assigning users to security groups...")
        admin_user = session.query(User).filter_by(username="admin").first()
        viewer_frysztak_user = (
            session.query(User).filter_by(username="viewer_frysztak").first()
        )
        viewer_radzilow_user = (
            session.query(User).filter_by(username="viewer_radzilow").first()
        )

        if admin_user and viewer_frysztak_user and viewer_radzilow_user:
            admin_group = (
                session.query(UserGroup).filter_by(system_key=ADMIN_GROUP_KEY).first()
            )
            staff_group = (
                session.query(UserGroup).filter_by(system_key=STAFF_GROUP_KEY).first()
            )

            if admin_group and staff_group:
                from app.modules.security.repositories import PermissionRepository

                repo = PermissionRepository(session)

                # Assign global admin to admin group
                repo.replace_user_groups(admin_user.id, {admin_group.id})
                # Assign viewers to staff group (read-only)
                repo.replace_user_groups(viewer_frysztak_user.id, {staff_group.id})
                repo.replace_user_groups(viewer_radzilow_user.id, {staff_group.id})

                session.commit()
                print("  ✓ Users assigned to groups")

        # Summary
        print("\n" + "=" * 60)
        print("✅ Database seeding completed successfully!")
        print("=" * 60)
        print("\n📊 Core Data:")
        print("  Organizations:      2")
        print("    - Gmina Frysztak")
        print("    - Gmina Radziłów")
        print("  Users:              3 (1 admin + 2 viewers)")
        print("  Water Objects:      4 (2 per organization)")
        print("    Gmina Frysztak:")
        print("      - Ujęcie wody - Jezioro Frysztak")
        print("      - Stacja uzdatniania wody Frysztak")
        print("    Gmina Radziłów:")
        print("      - Ujęcie wody - Rzeka Narew")
        print("      - Stacja uzdatniania wody Radziłów")
        print("  Devices:            4 (2 per organization)")
        print("  Measurement Points: 8")
        print(f"  Telemetry Packets:  {packets_created}")
        print("\n🔐 Security:")
        print(f"  Permissions:        {len(PERMISSION_CATALOG)}")
        print("  Groups:             2 (Admin + Staff)")
        print("  User Assignments:   3 users assigned to groups")
        print("\n🧑‍💻 Test Credentials:")
        print("\n  Global Admin (views all organizations):")
        print("    Username:         admin / password123")
        print("      → Full access to all organizations and data")
        print("      → Can manage users, devices, permissions")
        print("\n  Viewers (organization-specific):")
        print("    Gmina Frysztak:   viewer_frysztak / password123")
        print("      → Read-only access to Gmina Frysztak data")
        print("    Gmina Radziłów:   viewer_radzilow / password123")
        print("      → Read-only access to Gmina Radziłów data")


if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
