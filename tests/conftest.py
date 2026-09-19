"""
Test configuration for MANGANEX AI backend tests.

Uses a single shared in-memory SQLite database (via StaticPool) so all
connections during a test session see the same tables and data.
Completely isolated from the development database (dev.db).
"""

import sys
import os

# Add backend/ to PYTHONPATH so that 'app' package is importable
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ── Must import app.main AFTER sys.path is set ────────────────────────────────
from app.database import Base, get_db
from app.main import app  # also registers all models with Base.metadata

# ── In-memory engine shared across ALL connections in the test session ─────────
TEST_ENGINE = create_engine(
    "sqlite://",   # in-memory
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,   # StaticPool: single shared connection → same DB state
)
Base.metadata.create_all(bind=TEST_ENGINE)   # create all tables once

TestSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=TEST_ENGINE
)


def _override_get_db():
    """Dependency override that returns sessions backed by the in-memory engine."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Install the override globally (applies for the whole session) ─────────────
app.dependency_overrides[get_db] = _override_get_db


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def client():
    """
    TestClient using the dependency-overridden app (in-memory SQLite).
    """
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture()
def db():
    """Direct DB session for assertions (same in-memory engine)."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
