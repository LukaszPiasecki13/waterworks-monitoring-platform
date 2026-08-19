"""Telemetry query API tests.

Tests for org-isolation on API level were removed — routing and org
filtering now happens through /orgs/{org_id}/telemetry/... with
require_org_permission() dependency.
"""
