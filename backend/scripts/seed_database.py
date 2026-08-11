"""
Seed script to populate the database with test data.
Usage: python scripts/seed_database.py
"""

import sys
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from pathlib import Path

# Add the backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.infrastructure.sql.factory import SQLConnectionFactory
from app.modules.core_data.models.organization import Organization
from app.modules.core_data.models.user import User
from app.modules.core_data.models.water_object import WaterObject
from app.modules.core_data.models.device import Device
from app.modules.core_data.models.measurement_point import MeasurementPoint
from app.modules.telemetry.models.measurement_packet import TelemetryPacket
from app.modules.security.services.password import hash_password
from app.modules.security.permission_catalog import (
    ADMIN_GROUP_KEY,
    STAFF_GROUP_KEY,
    VIEW_PERMISSIONS,
    PERMISSION_CATALOG,
)
from app.modules.security.models import Permission, UserGroup
import json


def _seed_security(session: Session) -> tuple[int, int, UserGroup, UserGroup]:
    """Seed security permissions and groups. Returns (permissions_count, groups_count, admin_group, staff_group)."""
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
        view_permissions = session.query(Permission).filter(
            Permission.code.in_(VIEW_PERMISSIONS)
        ).all()
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
        settings.database_url,
        settings.database_schema
    )

    with Session(engine) as session:
        print("🌱 Starting database seeding...")

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
        print(f"  ✓ Created 2 organizations")

        # 2. Create Users
        print("\n👥 Creating users...")

        # Global admin (can see all organizations)
        admin_global = User(
            id=uuid4(),
            organization_id=None,
            username="admin",
            email="admin@waterworks.local",
            first_name="Adam",
            last_name="Administrator",
            hashed_password=hash_password("password123"),
            status="admin",
            is_active=True,
        )

        # Gmina Frysztak - viewer
        viewer_frysztak = User(
            id=uuid4(),
            organization_id=org1.id,
            username="viewer_frysztak",
            email="viewer@gmina-frysztak.pl",
            first_name="Stanisław",
            last_name="Obserwator",
            hashed_password=hash_password("password123"),
            status="regular",
            is_active=True,
        )

        # Gmina Radziłów - viewer
        viewer_radzilow = User(
            id=uuid4(),
            organization_id=org2.id,
            username="viewer_radzilow",
            email="viewer@gmina-radzilow.pl",
            first_name="Stefan",
            last_name="Obserwator",
            hashed_password=hash_password("password123"),
            status="regular",
            is_active=True,
        )

        session.add_all([admin_global, viewer_frysztak, viewer_radzilow])
        session.commit()
        print(f"  ✓ Created 3 users (1 admin + 2 viewers)")

        # 3. Create Water Objects
        print("\n💧 Creating water objects...")

        # Gmina Frysztak
        fr_intake = WaterObject(
            id=uuid4(),
            organization_id=org1.id,
            name="Ujęcie wody - Jezioro Frysztak",
            object_type="intake",
            location_description="Główne ujęcie wody powierzchniowej z jeziora Frysztak",
            latitude=50.1625,
            longitude=21.2483,
            is_active=True,
        )
        fr_treatment = WaterObject(
            id=uuid4(),
            organization_id=org1.id,
            name="Stacja uzdatniania wody Frysztak",
            object_type="water_treatment",
            location_description="Główna stacja uzdatniania wody, ul. Wodna 5, Frysztak",
            latitude=50.1630,
            longitude=21.2490,
            is_active=True,
        )

        # Gmina Radziłów
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
        rad_treatment = WaterObject(
            id=uuid4(),
            organization_id=org2.id,
            name="Stacja uzdatniania wody Radziłów",
            object_type="water_treatment",
            location_description="Stacja uzdatniania wody, ul. Słoneczna 12, Radziłów",
            latitude=52.9170,
            longitude=22.6840,
            is_active=True,
        )

        session.add_all([fr_intake, fr_treatment, rad_intake, rad_treatment])
        session.commit()
        print(f"  ✓ Created 4 water objects (2 per organization)")

        # 4. Create Devices
        print("\n📱 Creating devices...")

        # Gmina Frysztak devices
        dev_fr_intake = Device(
            id=uuid4(),
            water_object_id=fr_intake.id,
            external_id="FR-INTAKE-001",
            hashed_secret=hash_password("device_secret_123"),
            firmware_version="2.1.5",
            last_seen_at=datetime.now(timezone.utc),
            is_active=True,
        )
        dev_fr_treatment = Device(
            id=uuid4(),
            water_object_id=fr_treatment.id,
            external_id="FR-TREATMENT-001",
            hashed_secret=hash_password("device_secret_456"),
            firmware_version="2.0.3",
            last_seen_at=datetime.now(timezone.utc),
            is_active=True,
        )

        # Gmina Radziłów devices
        dev_rad_intake = Device(
            id=uuid4(),
            water_object_id=rad_intake.id,
            external_id="RAD-INTAKE-001",
            hashed_secret=hash_password("device_secret_789"),
            firmware_version="2.2.0",
            last_seen_at=datetime.now(timezone.utc),
            is_active=True,
        )
        dev_rad_treatment = Device(
            id=uuid4(),
            water_object_id=rad_treatment.id,
            external_id="RAD-TREATMENT-001",
            hashed_secret=hash_password("device_secret_012"),
            firmware_version="1.9.8",
            last_seen_at=datetime.now(timezone.utc),
            is_active=True,
        )

        session.add_all([dev_fr_intake, dev_fr_treatment, dev_rad_intake, dev_rad_treatment])
        session.commit()
        print(f"  ✓ Created 4 devices (2 per organization)")

        # 5. Create Measurement Points
        print("\n📊 Creating measurement points...")

        # Gmina Frysztak - Intake measurements
        mp_fr_intake_flow = MeasurementPoint(
            id=uuid4(),
            device_id=dev_fr_intake.id,
            external_id="FR-INTAKE-001-FLOW",
            point_type="flow_rate",
            unit="m³/h",
            min_technical=0.0,
            max_technical=300.0,
            is_active=True,
        )
        mp_fr_intake_temp = MeasurementPoint(
            id=uuid4(),
            device_id=dev_fr_intake.id,
            external_id="FR-INTAKE-001-TEMP",
            point_type="temperature",
            unit="°C",
            min_technical=2.0,
            max_technical=28.0,
            is_active=True,
        )

        # Gmina Frysztak - Water treatment measurements
        mp_fr_treatment_flow = MeasurementPoint(
            id=uuid4(),
            device_id=dev_fr_treatment.id,
            external_id="FR-TREATMENT-001-FLOW",
            point_type="flow_rate",
            unit="m³/h",
            min_technical=0.0,
            max_technical=300.0,
            is_active=True,
        )
        mp_fr_treatment_turbidity = MeasurementPoint(
            id=uuid4(),
            device_id=dev_fr_treatment.id,
            external_id="FR-TREATMENT-001-TURBIDITY",
            point_type="turbidity",
            unit="NTU",
            min_technical=0.0,
            max_technical=5.0,
            is_active=True,
        )

        # Gmina Radziłów - Intake measurements
        mp_rad_intake_flow = MeasurementPoint(
            id=uuid4(),
            device_id=dev_rad_intake.id,
            external_id="RAD-INTAKE-001-FLOW",
            point_type="flow_rate",
            unit="m³/h",
            min_technical=0.0,
            max_technical=350.0,
            is_active=True,
        )
        mp_rad_intake_temp = MeasurementPoint(
            id=uuid4(),
            device_id=dev_rad_intake.id,
            external_id="RAD-INTAKE-001-TEMP",
            point_type="temperature",
            unit="°C",
            min_technical=1.0,
            max_technical=30.0,
            is_active=True,
        )

        # Gmina Radziłów - Water treatment measurements
        mp_rad_treatment_flow = MeasurementPoint(
            id=uuid4(),
            device_id=dev_rad_treatment.id,
            external_id="RAD-TREATMENT-001-FLOW",
            point_type="flow_rate",
            unit="m³/h",
            min_technical=0.0,
            max_technical=350.0,
            is_active=True,
        )
        mp_rad_treatment_turbidity = MeasurementPoint(
            id=uuid4(),
            device_id=dev_rad_treatment.id,
            external_id="RAD-TREATMENT-001-TURBIDITY",
            point_type="turbidity",
            unit="NTU",
            min_technical=0.0,
            max_technical=5.0,
            is_active=True,
        )

        session.add_all([
            mp_fr_intake_flow, mp_fr_intake_temp,
            mp_fr_treatment_flow, mp_fr_treatment_turbidity,
            mp_rad_intake_flow, mp_rad_intake_temp,
            mp_rad_treatment_flow, mp_rad_treatment_turbidity
        ])
        session.commit()
        print(f"  ✓ Created 8 measurement points")

        # 6. Generate Telemetry Packets
        print("\n📡 Generating telemetry packets...")

        now = datetime.now(timezone.utc)
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
            (dev_fr_intake, org1.id, fr_intake.id, [
                ("FR-INTAKE-001-FLOW", lambda i: 180 + 60 * ((now.hour + i) % 24) / 24),
                ("FR-INTAKE-001-TEMP", lambda i: 12 + 8 * ((now.hour + i) % 24) / 24),
            ]),
            (dev_fr_treatment, org1.id, fr_treatment.id, [
                ("FR-TREATMENT-001-FLOW", lambda i: 175 + 60 * ((now.hour + i) % 24) / 24),
                ("FR-TREATMENT-001-TURBIDITY", lambda i: 0.3 + 0.2 * ((now.hour + i) % 24) / 24),
            ]),
            (dev_rad_intake, org2.id, rad_intake.id, [
                ("RAD-INTAKE-001-FLOW", lambda i: 200 + 70 * ((now.hour + i) % 24) / 24),
                ("RAD-INTAKE-001-TEMP", lambda i: 10 + 12 * ((now.hour + i) % 24) / 24),
            ]),
            (dev_rad_treatment, org2.id, rad_treatment.id, [
                ("RAD-TREATMENT-001-FLOW", lambda i: 195 + 70 * ((now.hour + i) % 24) / 24),
                ("RAD-TREATMENT-001-TURBIDITY", lambda i: 0.4 + 0.25 * ((now.hour + i) % 24) / 24),
            ]),
        ]

        for device, org_id, obj_id, measurements in devices:
            # Generate 100 packets per device over the past 7 days
            for i in range(100):
                timestamp = now - timedelta(hours=i)

                # Build points array with correct structure
                points = []
                for mpoint_id, measurement_func in measurements:
                    if mpoint_id in measurement_point_map:
                        mp_info = measurement_point_map[mpoint_id]
                        points.append({
                            "point_id": mp_info["id"],
                            "type": mp_info["type"],
                            "unit": mp_info["unit"],
                            "value": measurement_func(i),
                            "quality": "good" if i % 10 != 0 else "warning",
                        })

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
                        }
                    }
                )
                session.add(packet)
                packets_created += 1

            session.commit()

        print(f"  ✓ Created {packets_created} telemetry packets")

        # Assign users to groups
        print("\n👥 Assigning users to security groups...")
        admin_user = session.query(User).filter_by(username="admin").first()
        viewer_frysztak_user = session.query(User).filter_by(username="viewer_frysztak").first()
        viewer_radzilow_user = session.query(User).filter_by(username="viewer_radzilow").first()

        if admin_user and viewer_frysztak_user and viewer_radzilow_user:
            admin_group = session.query(UserGroup).filter_by(
                system_key=ADMIN_GROUP_KEY
            ).first()
            staff_group = session.query(UserGroup).filter_by(
                system_key=STAFF_GROUP_KEY
            ).first()

            if admin_group and staff_group:
                from app.modules.security.repositories import PermissionRepository
                repo = PermissionRepository(session)

                # Assign global admin to admin group
                repo.replace_user_groups(admin_user.id, {admin_group.id})
                # Assign viewers to staff group (read-only)
                repo.replace_user_groups(viewer_frysztak_user.id, {staff_group.id})
                repo.replace_user_groups(viewer_radzilow_user.id, {staff_group.id})

                session.commit()
                print(f"  ✓ Users assigned to groups")

        # Summary
        print("\n" + "="*60)
        print("✅ Database seeding completed successfully!")
        print("="*60)
        print("\n📊 Core Data:")
        print(f"  Organizations:      2")
        print(f"    - Gmina Frysztak")
        print(f"    - Gmina Radziłów")
        print(f"  Users:              3 (1 admin + 2 viewers)")
        print(f"  Water Objects:      4 (2 per organization)")
        print(f"    Gmina Frysztak:")
        print(f"      - Ujęcie wody - Jezioro Frysztak")
        print(f"      - Stacja uzdatniania wody Frysztak")
        print(f"    Gmina Radziłów:")
        print(f"      - Ujęcie wody - Rzeka Narew")
        print(f"      - Stacja uzdatniania wody Radziłów")
        print(f"  Devices:            4 (2 per organization)")
        print(f"  Measurement Points: 8")
        print(f"  Telemetry Packets:  {packets_created}")
        print("\n🔐 Security:")
        print(f"  Permissions:        {len(PERMISSION_CATALOG)}")
        print(f"  Groups:             2 (Admin + Staff)")
        print(f"  User Assignments:   3 users assigned to groups")
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
