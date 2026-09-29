from __future__ import annotations
from datetime import date, datetime
from enum import Enum
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class PipelineType(str, Enum):
    PENNY="PENNY"; COMPOUNDER="COMPOUNDER"; AGENT_SECURITY="AGENT_SECURITY"; WATCH_ONLY="WATCH_ONLY"; EXCLUDED="EXCLUDED"

class CompanyStatus(str, Enum):
    NEW="NEW"; RESEARCH="RESEARCH"; WATCH_CLOSELY="WATCH_CLOSELY"; CORE_WATCH="CORE_WATCH"; MOMENTUM_ONLY="MOMENTUM_ONLY"; DILUTION_RISK="DILUTION_RISK"; PAUSED="PAUSED"; EXCLUDED="EXCLUDED"

class Company(Base):
    __tablename__="companies"
    id: Mapped[int]=mapped_column(primary_key=True)
    ticker: Mapped[str]=mapped_column(String(16),unique=True,index=True)
    company_name: Mapped[str|None]=mapped_column(String(255))
    exchange: Mapped[str|None]=mapped_column(String(32))
    sector: Mapped[str|None]=mapped_column(String(128))
    industry: Mapped[str|None]=mapped_column(String(128))
    pipeline_type: Mapped[str]=mapped_column(String(32),default=PipelineType.WATCH_ONLY.value)
    status: Mapped[str]=mapped_column(String(32),default=CompanyStatus.NEW.value)
    market_cap: Mapped[float|None]=mapped_column(Float)
    description: Mapped[str|None]=mapped_column(Text)
    website: Mapped[str|None]=mapped_column(String(512))
    cik: Mapped[str|None]=mapped_column(String(32))
    exclusion_reason: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    updated_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    snapshots: Mapped[list["DailySnapshot"]]=relationship(back_populates="company",cascade="all, delete-orphan")
    thesis: Mapped["ResearchThesis|None"]=relationship(back_populates="company",uselist=False,cascade="all, delete-orphan")

class DailySnapshot(Base):
    __tablename__="daily_snapshots"
    __table_args__=(UniqueConstraint("company_id","snapshot_date",name="uq_company_snapshot_date"),)
    id: Mapped[int]=mapped_column(primary_key=True)
    company_id: Mapped[int]=mapped_column(ForeignKey("companies.id"),index=True)
    snapshot_date: Mapped[date]=mapped_column(Date,index=True)
    price: Mapped[float|None]=mapped_column(Float)
    previous_close: Mapped[float|None]=mapped_column(Float)
    daily_change_pct: Mapped[float|None]=mapped_column(Float)
    five_day_change_pct: Mapped[float|None]=mapped_column(Float)
    twenty_day_change_pct: Mapped[float|None]=mapped_column(Float)
    volume: Mapped[float|None]=mapped_column(Float)
    avg_volume_20d: Mapped[float|None]=mapped_column(Float)
    volume_ratio: Mapped[float|None]=mapped_column(Float)
    market_cap: Mapped[float|None]=mapped_column(Float)
    enterprise_value: Mapped[float|None]=mapped_column(Float)
    cash: Mapped[float|None]=mapped_column(Float)
    debt: Mapped[float|None]=mapped_column(Float)
    shares_outstanding: Mapped[float|None]=mapped_column(Float)
    news_count: Mapped[int]=mapped_column(Integer,default=0)
    filing_count: Mapped[int]=mapped_column(Integer,default=0)
    thesis_status: Mapped[str|None]=mapped_column(String(32))
    trend_status: Mapped[str|None]=mapped_column(String(32))
    notes: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
    company: Mapped[Company]=relationship(back_populates="snapshots")

class ResearchThesis(Base):
    __tablename__="research_theses"
    id: Mapped[int]=mapped_column(primary_key=True)
    company_id: Mapped[int]=mapped_column(ForeignKey("companies.id"),unique=True)
    technology_summary: Mapped[str|None]=mapped_column(Text)
    business_summary: Mapped[str|None]=mapped_column(Text)
    bull_case: Mapped[str|None]=mapped_column(Text)
    base_case: Mapped[str|None]=mapped_column(Text)
    bear_case: Mapped[str|None]=mapped_column(Text)
    key_catalysts: Mapped[str|None]=mapped_column(Text)
    key_risks: Mapped[str|None]=mapped_column(Text)
    technology_score: Mapped[float|None]=mapped_column(Float)
    management_score: Mapped[float|None]=mapped_column(Float)
    financial_score: Mapped[float|None]=mapped_column(Float)
    capital_structure_score: Mapped[float|None]=mapped_column(Float)
    catalyst_score: Mapped[float|None]=mapped_column(Float)
    cash_runway_months: Mapped[float|None]=mapped_column(Float)
    thesis_status: Mapped[str|None]=mapped_column(String(32))
    thesis_version: Mapped[int]=mapped_column(Integer,default=1)
    updated_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    company: Mapped[Company]=relationship(back_populates="thesis")

class CapitalStructure(Base):
    __tablename__="capital_structures"
    __table_args__=(UniqueConstraint("company_id","as_of_date",name="uq_company_capital_date"),)
    id: Mapped[int]=mapped_column(primary_key=True)
    company_id: Mapped[int]=mapped_column(ForeignKey("companies.id"),index=True)
    as_of_date: Mapped[date]=mapped_column(Date)
    common_shares: Mapped[float|None]=mapped_column(Float)
    preferred_shares: Mapped[float|None]=mapped_column(Float)
    warrants_count: Mapped[float|None]=mapped_column(Float)
    warrant_avg_strike: Mapped[float|None]=mapped_column(Float)
    options_count: Mapped[float|None]=mapped_column(Float)
    rsus_count: Mapped[float|None]=mapped_column(Float)
    convertible_debt: Mapped[float|None]=mapped_column(Float)
    convertible_shares: Mapped[float|None]=mapped_column(Float)
    atm_remaining: Mapped[float|None]=mapped_column(Float)
    shelf_capacity: Mapped[float|None]=mapped_column(Float)
    fully_diluted_shares: Mapped[float|None]=mapped_column(Float)
    fully_diluted_market_cap: Mapped[float|None]=mapped_column(Float)
    reverse_split_count_5y: Mapped[int]=mapped_column(Integer,default=0)
    last_reverse_split_date: Mapped[date|None]=mapped_column(Date)
    dilution_risk: Mapped[str|None]=mapped_column(String(16))
    notes: Mapped[str|None]=mapped_column(Text)

class Catalyst(Base):
    __tablename__="catalysts"
    id: Mapped[int]=mapped_column(primary_key=True)
    company_id: Mapped[int]=mapped_column(ForeignKey("companies.id"),index=True)
    type: Mapped[str]=mapped_column(String(64))
    title: Mapped[str]=mapped_column(String(255))
    description: Mapped[str|None]=mapped_column(Text)
    expected_date: Mapped[date|None]=mapped_column(Date,index=True)
    actual_date: Mapped[date|None]=mapped_column(Date)
    status: Mapped[str]=mapped_column(String(32),default="EXPECTED")
    impact: Mapped[str|None]=mapped_column(String(32))
    source_url: Mapped[str|None]=mapped_column(String(1024))

class Person(Base):
    __tablename__="people"
    id: Mapped[int]=mapped_column(primary_key=True)
    name: Mapped[str]=mapped_column(String(255),unique=True)
    bio: Mapped[str|None]=mapped_column(Text)
    notes: Mapped[str|None]=mapped_column(Text)

class CompanyPerson(Base):
    __tablename__="company_people"
    __table_args__=(UniqueConstraint("company_id","person_id","role",name="uq_company_person_role"),)
    id: Mapped[int]=mapped_column(primary_key=True)
    company_id: Mapped[int]=mapped_column(ForeignKey("companies.id"),index=True)
    person_id: Mapped[int]=mapped_column(ForeignKey("people.id"),index=True)
    role: Mapped[str]=mapped_column(String(128))
    founder: Mapped[bool]=mapped_column(Boolean,default=False)
    current: Mapped[bool]=mapped_column(Boolean,default=True)
    ownership_pct: Mapped[float|None]=mapped_column(Float)
    credibility_notes: Mapped[str|None]=mapped_column(Text)
    success_history: Mapped[str|None]=mapped_column(Text)
    failure_history: Mapped[str|None]=mapped_column(Text)
    regulatory_history: Mapped[str|None]=mapped_column(Text)

class PersonFlag(Base):
    __tablename__="person_flags"
    id: Mapped[int]=mapped_column(primary_key=True)
    person_id: Mapped[int]=mapped_column(ForeignKey("people.id"),index=True)
    flag_type: Mapped[str]=mapped_column(String(64))
    reason: Mapped[str]=mapped_column(Text)
    source: Mapped[str|None]=mapped_column(String(1024))
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)

class ResearchSource(Base):
    __tablename__="research_sources"
    id: Mapped[int]=mapped_column(primary_key=True)
    company_id: Mapped[int]=mapped_column(ForeignKey("companies.id"),index=True)
    source_type: Mapped[str]=mapped_column(String(64))
    title: Mapped[str]=mapped_column(String(512))
    url: Mapped[str]=mapped_column(String(1024))
    publisher: Mapped[str|None]=mapped_column(String(255))
    published_date: Mapped[date|None]=mapped_column(Date)
    summary: Mapped[str|None]=mapped_column(Text)
    raw_excerpt: Mapped[str|None]=mapped_column(Text)
    importance: Mapped[str|None]=mapped_column(String(32))
    created_at: Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
