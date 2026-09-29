from datetime import date, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app import models

def get_company(db: Session, ticker: str):
    return db.scalar(select(models.Company).where(models.Company.ticker==ticker.upper()))

def list_companies(db: Session, pipeline: str|None=None, status: str|None=None):
    stmt=select(models.Company).order_by(models.Company.ticker)
    if pipeline: stmt=stmt.where(models.Company.pipeline_type==pipeline)
    if status: stmt=stmt.where(models.Company.status==status)
    return list(db.scalars(stmt))

def add_company(db: Session, ticker: str, pipeline: str, reason: str|None=None):
    ticker=ticker.upper(); existing=get_company(db,ticker)
    if existing: return existing
    row=models.Company(ticker=ticker,pipeline_type=pipeline,status=models.CompanyStatus.NEW.value,description=reason)
    db.add(row); db.commit(); db.refresh(row); return row

def update_status(db: Session, ticker: str, status: str, reason: str|None=None):
    row=get_company(db,ticker)
    if not row: raise ValueError(f"Unknown ticker: {ticker}")
    row.status=status
    if reason: row.description=((row.description or "")+"\nStatus note: "+reason).strip()
    db.commit(); db.refresh(row); return row

def save_snapshot(db: Session, ticker: str, snapshot_date: date, **values):
    company=get_company(db,ticker)
    if not company: raise ValueError(f"Unknown ticker: {ticker}")
    row=db.scalar(select(models.DailySnapshot).where(models.DailySnapshot.company_id==company.id,models.DailySnapshot.snapshot_date==snapshot_date))
    if not row:
        row=models.DailySnapshot(company_id=company.id,snapshot_date=snapshot_date); db.add(row)
    for key,value in values.items():
        if hasattr(row,key): setattr(row,key,value)
    db.commit(); db.refresh(row); return row

def stock_history(db: Session, ticker: str, days: int=30):
    company=get_company(db,ticker)
    if not company: raise ValueError(f"Unknown ticker: {ticker}")
    since=date.today()-timedelta(days=days)
    stmt=select(models.DailySnapshot).where(models.DailySnapshot.company_id==company.id,models.DailySnapshot.snapshot_date>=since).order_by(models.DailySnapshot.snapshot_date)
    return list(db.scalars(stmt))

def upsert_thesis(db: Session, ticker: str, **values):
    company=get_company(db,ticker)
    if not company: raise ValueError(f"Unknown ticker: {ticker}")
    row=db.scalar(select(models.ResearchThesis).where(models.ResearchThesis.company_id==company.id))
    if not row: row=models.ResearchThesis(company_id=company.id); db.add(row)
    for key,value in values.items():
        if value is not None and hasattr(row,key): setattr(row,key,value)
    row.thesis_version=(row.thesis_version or 0)+1
    db.commit(); db.refresh(row); return row

def add_catalyst(db: Session, ticker: str, **values):
    company=get_company(db,ticker)
    if not company: raise ValueError(f"Unknown ticker: {ticker}")
    row=models.Catalyst(company_id=company.id,**values); db.add(row); db.commit(); db.refresh(row); return row

def upcoming_catalysts(db: Session, days: int=30):
    today=date.today()
    stmt=select(models.Catalyst,models.Company.ticker).join(models.Company).where(models.Catalyst.expected_date>=today,models.Catalyst.expected_date<=today+timedelta(days=days)).order_by(models.Catalyst.expected_date)
    return list(db.execute(stmt).all())

def add_source(db: Session, ticker: str, **values):
    company=get_company(db,ticker)
    if not company: raise ValueError(f"Unknown ticker: {ticker}")
    row=models.ResearchSource(company_id=company.id,**values); db.add(row); db.commit(); db.refresh(row); return row
