from datetime import date
from typing import Any
from mcp.server import MCPServer
from app.database import SessionLocal
from app import repository

mcp = MCPServer("Stock Research MCP")

def company_dict(c):
    return {"ticker":c.ticker,"company_name":c.company_name,"pipeline_type":c.pipeline_type,"status":c.status,"market_cap":c.market_cap,"description":c.description,"exclusion_reason":c.exclusion_reason}

@mcp.tool()
def list_watchlist(pipeline: str|None=None, status: str|None=None) -> list[dict[str,Any]]:
    """List companies in the persistent research watchlist."""
    with SessionLocal() as db:
        return [company_dict(c) for c in repository.list_companies(db,pipeline,status)]

@mcp.tool()
def get_company(ticker: str) -> dict[str,Any]:
    """Get a company plus latest snapshot and current thesis."""
    with SessionLocal() as db:
        c=repository.get_company(db,ticker)
        if not c: raise ValueError(f"Unknown ticker: {ticker}")
        history=repository.stock_history(db,ticker,3650); latest=history[-1] if history else None; thesis=c.thesis
        return {"company":company_dict(c),
                "latest_snapshot":None if not latest else {"date":latest.snapshot_date.isoformat(),"price":latest.price,"daily_change_pct":latest.daily_change_pct,"five_day_change_pct":latest.five_day_change_pct,"volume_ratio":latest.volume_ratio,"trend_status":latest.trend_status,"notes":latest.notes},
                "thesis":None if not thesis else {"technology_summary":thesis.technology_summary,"business_summary":thesis.business_summary,"bull_case":thesis.bull_case,"bear_case":thesis.bear_case,"key_catalysts":thesis.key_catalysts,"key_risks":thesis.key_risks,"cash_runway_months":thesis.cash_runway_months,"thesis_status":thesis.thesis_status,"thesis_version":thesis.thesis_version}}

@mcp.tool()
def get_stock_history(ticker: str, days: int=30) -> list[dict[str,Any]]:
    """Return stored daily snapshots for a ticker."""
    with SessionLocal() as db:
        rows=repository.stock_history(db,ticker,days)
        return [{"date":x.snapshot_date.isoformat(),"price":x.price,"daily_change_pct":x.daily_change_pct,"five_day_change_pct":x.five_day_change_pct,"volume":x.volume,"volume_ratio":x.volume_ratio,"market_cap":x.market_cap,"trend_status":x.trend_status,"notes":x.notes} for x in rows]

@mcp.tool()
def add_candidate(ticker: str, pipeline: str, reason: str="") -> dict[str,Any]:
    """Add a newly discovered stock candidate without automatically promoting it."""
    with SessionLocal() as db: return company_dict(repository.add_company(db,ticker,pipeline,reason))

@mcp.tool()
def update_company_status(ticker: str, status: str, reason: str="") -> dict[str,Any]:
    """Move a stock through the research pipeline and preserve the reason."""
    with SessionLocal() as db: return company_dict(repository.update_status(db,ticker,status,reason))

@mcp.tool()
def save_daily_snapshot(ticker: str,snapshot_date: str,price: float|None=None,daily_change_pct: float|None=None,five_day_change_pct: float|None=None,twenty_day_change_pct: float|None=None,volume: float|None=None,avg_volume_20d: float|None=None,volume_ratio: float|None=None,market_cap: float|None=None,cash: float|None=None,debt: float|None=None,trend_status: str|None=None,thesis_status: str|None=None,notes: str|None=None) -> dict[str,Any]:
    """Save or update a daily research snapshot."""
    values=locals().copy(); ticker_value=values.pop("ticker"); date_value=date.fromisoformat(values.pop("snapshot_date"))
    with SessionLocal() as db:
        row=repository.save_snapshot(db,ticker_value,date_value,**values)
        return {"ticker":ticker_value.upper(),"date":row.snapshot_date.isoformat(),"id":row.id}

@mcp.tool()
def update_thesis(ticker: str,technology_summary: str|None=None,business_summary: str|None=None,bull_case: str|None=None,base_case: str|None=None,bear_case: str|None=None,key_catalysts: str|None=None,key_risks: str|None=None,cash_runway_months: float|None=None,thesis_status: str|None=None) -> dict[str,Any]:
    """Create or update the persistent research thesis for a ticker."""
    values=locals().copy(); ticker_value=values.pop("ticker")
    with SessionLocal() as db:
        row=repository.upsert_thesis(db,ticker_value,**values)
        return {"ticker":ticker_value.upper(),"thesis_version":row.thesis_version,"thesis_status":row.thesis_status}

@mcp.tool()
def add_catalyst(ticker: str,type: str,title: str,expected_date: str|None=None,description: str|None=None,impact: str|None=None,source_url: str|None=None) -> dict[str,Any]:
    """Record an expected or realized catalyst."""
    with SessionLocal() as db:
        row=repository.add_catalyst(db,ticker,type=type,title=title,description=description,expected_date=date.fromisoformat(expected_date) if expected_date else None,impact=impact,source_url=source_url)
        return {"id":row.id,"ticker":ticker.upper(),"title":row.title}

@mcp.tool()
def list_upcoming_catalysts(days: int=30) -> list[dict[str,Any]]:
    """List expected catalysts across the watchlist."""
    with SessionLocal() as db:
        return [{"ticker":ticker,"type":row.type,"title":row.title,"expected_date":row.expected_date.isoformat() if row.expected_date else None,"impact":row.impact} for row,ticker in repository.upcoming_catalysts(db,days)]

@mcp.tool()
def add_research_source(ticker: str,source_type: str,title: str,url: str,publisher: str|None=None,published_date: str|None=None,summary: str|None=None,importance: str|None=None) -> dict[str,Any]:
    """Attach a research source while preserving provenance."""
    with SessionLocal() as db:
        row=repository.add_source(db,ticker,source_type=source_type,title=title,url=url,publisher=publisher,published_date=date.fromisoformat(published_date) if published_date else None,summary=summary,importance=importance)
        return {"id":row.id,"ticker":ticker.upper(),"title":title}


@mcp.tool()
def update_capital_structure(ticker: str,as_of_date: str,common_shares: float|None=None,preferred_shares: float|None=None,warrants_count: float|None=None,warrant_avg_strike: float|None=None,options_count: float|None=None,rsus_count: float|None=None,convertible_debt: float|None=None,convertible_shares: float|None=None,atm_remaining: float|None=None,shelf_capacity: float|None=None,fully_diluted_shares: float|None=None,fully_diluted_market_cap: float|None=None,reverse_split_count_5y: int|None=None,last_reverse_split_date: str|None=None,dilution_risk: str|None=None,notes: str|None=None) -> dict[str,Any]:
    """Create or update a dated capital-structure record."""
    values=locals().copy(); ticker_value=values.pop("ticker"); asof=date.fromisoformat(values.pop("as_of_date"))
    last_rs=values.pop("last_reverse_split_date")
    values["last_reverse_split_date"]=date.fromisoformat(last_rs) if last_rs else None
    with SessionLocal() as db:
        row=repository.upsert_capital_structure(db,ticker_value,asof,**values)
        return {"id":row.id,"ticker":ticker_value.upper(),"as_of_date":row.as_of_date.isoformat(),"dilution_risk":row.dilution_risk}

@mcp.tool()
def get_management_history(ticker: str) -> list[dict[str,Any]]:
    """Return stored founder/executive history for a company."""
    with SessionLocal() as db:
        rows=repository.management_history(db,ticker)
        return [{"name":person.name,"role":link.role,"founder":link.founder,"current":link.current,"ownership_pct":link.ownership_pct,"credibility_notes":link.credibility_notes,"success_history":link.success_history,"failure_history":link.failure_history,"regulatory_history":link.regulatory_history} for link,person in rows]
