"""Telemetry query security tests.

Tests for org-isolation on service level were removed — org filtering
now happens through /orgs/{org_id}/telemetry/... with require_org_permission()
dependency checking both membership and permissions.
"""
