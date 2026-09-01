"""Command-line interface for administrative tasks."""

import sys

import click
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import create_session
from app.modules.core_data.repositories.users import UserRepository
from app.modules.security.permission_catalog import ADMIN_GROUP_KEY
from app.modules.security.repositories.permissions import PermissionRepository
from app.modules.security.services.password import hash_password
from app.modules.telemetry.repositories.partitions import (
    MONTHS_AHEAD,
    MONTHS_BACK,
    ensure_measurement_partitions,
)


@click.group()
def cli():
    """Waterworks monitoring platform administration."""
    pass


@cli.command()
@click.option("--username", prompt="Username", help="Username for superadmin account")
@click.option("--email", prompt="Email", help="Email for superadmin account")
def create_superadmin(username: str, email: str):
    """Create a platform superadmin account and assign to Super Admin group."""
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)

    session = create_session()

    try:
        user_repo = UserRepository(session)
        perm_repo = PermissionRepository(session)

        # Ensure Super Admin group exists (should be seeded at startup)
        super_admin_group = perm_repo.get_group_by_system_key(
            ADMIN_GROUP_KEY, organization_id=None
        )
        if not super_admin_group:
            click.echo(
                "Error: Super Admin group not found. Run application once to seed it.",
                err=True,
            )
            sys.exit(1)

        # Check if user already exists
        existing_user = user_repo.get_by_username(username)
        if existing_user:
            # If exists, check if already in Super Admin group
            user_groups = set(perm_repo.group_ids_for_user(existing_user.id))
            if super_admin_group.id in user_groups:
                click.echo(f"User '{username}' is already a superadmin.")
            else:
                # Add to Super Admin group
                perm_repo.replace_user_groups(
                    existing_user.id, user_groups | {super_admin_group.id}
                )
                session.commit()
                click.echo(f"User '{username}' added to Super Admin group.")
            session.close()
            return

        # Create new user (without organization_id or status — they were removed)
        hashed_password = hash_password(password)
        user = user_repo.create(
            username=username,
            email=email,
            hashed_password=hashed_password,
            first_name="",
            last_name="",
            is_active=True,
        )
        session.flush()
        session.refresh(user)

        # Assign to Super Admin group
        perm_repo.replace_user_groups(user.id, {super_admin_group.id})
        session.commit()

        click.echo(f"Superadmin account created: {username} ({email})")

    except IntegrityError:
        session.rollback()
        click.echo("Error: Email or username already exists.", err=True)
        sys.exit(1)
    except Exception as e:
        session.rollback()
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    finally:
        session.close()


@cli.command("ensure-measurement-partitions")
@click.option(
    "--months-back",
    default=MONTHS_BACK,
    show_default=True,
    help="How many past months to cover.",
)
@click.option(
    "--months-ahead",
    default=MONTHS_AHEAD,
    show_default=True,
    help="How many future months to create in advance.",
)
def ensure_measurement_partitions_command(months_back: int, months_ahead: int):
    """Create the monthly partitions of the `measurements` table.

    Runs on every application startup as well; this command exists for
    maintenance windows where the application is not being restarted.
    """
    session = create_session()

    try:
        created = ensure_measurement_partitions(
            session, months_back=months_back, months_ahead=months_ahead
        )
        session.commit(skip_audit=True)
    except Exception as e:
        session.rollback()
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    finally:
        session.close()

    click.echo(f"Partitions present: {len(created)}")
    for partition in created:
        click.echo(f"  {partition}")


if __name__ == "__main__":
    cli()
