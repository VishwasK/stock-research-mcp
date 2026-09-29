from app.database import Base, SessionLocal, engine
from app import models, repository

PENNY=["ARAY","ALDX","ONCO","AIFF","SDEV","MGLD","GLND","GANX","OSTX","DFLI","HYFT","SCYX","ANNX"]
COMPOUNDER=["TMDX","LEU","VKTX","RCAT","RDW","MYRG","POWL","UUUU","MWA","FLNC","S","VRNS","TENB","SAIL"]
EXCLUDED=["BENF","LHSW","TDIC"]

def seed():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        for ticker in PENNY:
            c=repository.add_company(db,ticker,models.PipelineType.PENNY.value,"Seeded from penny/asymmetric research pipeline")
            if c.status==models.CompanyStatus.NEW.value: c.status=models.CompanyStatus.RESEARCH.value
        for ticker in COMPOUNDER:
            c=repository.add_company(db,ticker,models.PipelineType.COMPOUNDER.value,"Seeded from next-compounder research pipeline")
            if c.status==models.CompanyStatus.NEW.value: c.status=models.CompanyStatus.RESEARCH.value
        for ticker in EXCLUDED:
            c=repository.add_company(db,ticker,models.PipelineType.EXCLUDED.value,"User investment-screen preference")
            c.status=models.CompanyStatus.EXCLUDED.value
            c.exclusion_reason="USER_PREFERENCE — exclusion is not an allegation of misconduct."
        db.commit()

if __name__=="__main__":
    seed(); print("Seed complete")
