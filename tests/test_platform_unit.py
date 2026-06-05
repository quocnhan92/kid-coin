"""Platform unit tests — no database required (H3, H6)."""
import uuid

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.core.api_compat import API_VERSION, check_client_version, compare_versions
from app.core.tenant import assert_same_family


class TestApiCompat:
    def test_compare_versions_ordering(self):
        assert compare_versions("1.0.0", "1.0.1") < 0
        assert compare_versions("2.0.0", "1.9.9") > 0
        assert compare_versions("1.0", "1.0.0") == 0

    def test_compare_versions_empty_segments(self):
        assert compare_versions("1", "1.0.0") == 0

    def test_check_client_version_rejects_old(self):
        scope = {
            "type": "http",
            "headers": [(b"x-client-version", b"0.0.1")],
            "method": "GET",
            "path": "/api/v1/system/health",
        }
        with pytest.raises(HTTPException) as exc:
            check_client_version(Request(scope))
        assert exc.value.status_code == 426

    def test_check_client_version_allows_missing_header(self):
        scope = {"type": "http", "headers": [], "method": "GET", "path": "/"}
        check_client_version(Request(scope))

    def test_api_version_constant(self):
        assert API_VERSION == "1"


class TestTenantGuard:
    def test_assert_same_family_ok(self):
        fid = uuid.uuid4()
        assert_same_family(fid, fid)

    def test_assert_same_family_denied(self):
        with pytest.raises(HTTPException) as exc:
            assert_same_family(uuid.uuid4(), uuid.uuid4())
        assert exc.value.status_code == 403

    def test_assert_same_family_empty_uuid(self):
        fid = uuid.uuid4()
        with pytest.raises(HTTPException):
            assert_same_family(uuid.uuid4(), fid)
