import os
from app.config import Settings

def test_sqlite_fallback(monkeypatch):
    monkeypatch.delenv("JAWSDB_URL",raising=False)
    monkeypatch.delenv("DATABASE_URL",raising=False)
    s=Settings(_env_file=None)
    assert s.resolved_database_url.startswith("sqlite")

def test_jawsdb_url_conversion(monkeypatch):
    monkeypatch.setenv("JAWSDB_URL","mysql://u:p@host/db")
    s=Settings(_env_file=None)
    assert s.resolved_database_url=="mysql+pymysql://u:p@host/db"
