# Stock Research MCP

Persistent research ledger + MCP server for the daily penny-stock and next-compounder research pipelines.

## Phase 1 + 2 scope

This first build intentionally does **not** fetch market data or automate trading. It provides:

- database-agnostic SQLAlchemy persistence
- SQLite locally
- JawsDB MySQL on Heroku via `JAWSDB_URL`
- FastAPI health/debug endpoints
- MCP v2 Streamable HTTP endpoint at `/mcp/`
- bearer-token protection for MCP
- companies/watchlists
- daily snapshots
- research theses
- catalysts
- capital-structure schema
- founder/management and provenance schema
- seeded penny/compounder/exclusion lists
- repository tests

The reasoning layer remains ChatGPT. The service stores facts and history.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m scripts.seed_watchlist
uvicorn app.main:app --reload
```

Health:

```bash
curl http://127.0.0.1:8000/health
```

MCP endpoint:

```text
http://127.0.0.1:8000/mcp/
```

Send `Authorization: Bearer <MCP_API_KEY>`.

## Database selection

Resolution order:

1. `JAWSDB_URL`
2. `DATABASE_URL`
3. local `sqlite:///./stock_research.db`

A JawsDB URL beginning with `mysql://` is automatically converted to SQLAlchemy's `mysql+pymysql://` driver.

## MCP tools

- `list_watchlist`
- `get_company`
- `get_stock_history`
- `add_candidate`
- `update_company_status`
- `save_daily_snapshot`
- `update_thesis`
- `add_catalyst`
- `list_upcoming_catalysts`
- `add_research_source`

## Seed universe

Penny/asymmetric:
ARAY, ALDX, ONCO, AIFF, SDEV, MGLD, GLND, GANX, OSTX, DFLI, HYFT, SCYX, ANNX.

Next compounders:
TMDX, LEU, VKTX, RCAT, RDW, MYRG, POWL, UUUU, MWA, FLNC, S, VRNS, TENB, SAIL.

Excluded by user investment-screen preference:
BENF, LHSW, TDIC. This is stored explicitly as a user preference, **not an allegation of misconduct**.

## Heroku

```bash
heroku addons:create jawsdb
heroku config:set MCP_API_KEY='<strong-random-secret>'
git push heroku main
heroku run python -m scripts.seed_watchlist
```

The Procfile runs Alembic migrations during the release phase.

## Tests

```bash
pytest
```

## Next phases

- Phase 3: pluggable market-data provider + daily refresh
- Phase 4: SEC intelligence for ATM/S-3/424B/warrants/convertibles/reverse splits/share-count changes
- Phase 5: morning-pipeline context + new-candidate discovery
- Phase 6: optional dashboard

No brokerage integration or automated trading is planned.

CI validates tests, seed execution, and application import on Python 3.12.
