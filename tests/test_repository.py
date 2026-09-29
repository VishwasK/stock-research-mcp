from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app import models, repository

def make_db():
    engine=create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine,expire_on_commit=False)()

def test_watchlist_crud_and_history():
    db=make_db()
    c=repository.add_company(db,"GANX",models.PipelineType.PENNY.value,"test")
    assert c.ticker=="GANX"
    assert [x.ticker for x in repository.list_companies(db,models.PipelineType.PENNY.value)]==["GANX"]
    repository.update_status(db,"GANX",models.CompanyStatus.WATCH_CLOSELY.value,"science improving")
    assert repository.get_company(db,"GANX").status==models.CompanyStatus.WATCH_CLOSELY.value
    repository.save_snapshot(db,"GANX",date.today(),price=1.72,volume_ratio=2.5,trend_status="STABLE")
    history=repository.stock_history(db,"GANX",7)
    assert len(history)==1 and history[0].price==1.72

def test_thesis_catalyst_and_source():
    db=make_db()
    repository.add_company(db,"OSTX",models.PipelineType.PENNY.value)
    thesis=repository.upsert_thesis(db,"OSTX",technology_summary="OST-HER2",thesis_status="RESEARCH")
    assert thesis.technology_summary=="OST-HER2"
    catalyst=repository.add_catalyst(db,"OSTX",type="FDA",title="Pre-BLA meeting",expected_date=date.today(),impact="HIGH")
    assert catalyst.title=="Pre-BLA meeting"
    assert repository.upcoming_catalysts(db,30)[0][1]=="OSTX"
    source=repository.add_source(db,"OSTX",source_type="SEC",title="10-Q",url="https://example.com/10q",summary="Financing details")
    assert source.source_type=="SEC"
