"""
conftest.py
-----------
Top-level pytest fixtures.

Mocks lib.database so the test suite works without real Google credentials.
The mock is installed via sys.modules *before* any server/lib code is imported,
preventing the credential-loading side-effects in lib/database.py.
"""

import sys
import types
from unittest.mock import MagicMock

# Build a fake lib.database module with a mock db_client
_fake_db_module = types.ModuleType("lib.database")
_mock_db_client = MagicMock()
_fake_db_module.db_client = _mock_db_client
_fake_db_module.db = MagicMock()
sys.modules["lib.database"] = _fake_db_module
