from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.database import Base, engine
from app.mcp_server import mcp

settings=get_settings()
mcp_app=mcp.streamable_http_app(streamable_http_path="/",stateless_http=True,json_response=True,host="0.0.0.0")

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    async with mcp.session_manager.run():
        yield

app=FastAPI(title="Stock Research MCP",version="0.1.0",lifespan=lifespan)

@app.middleware("http")
async def protect_mcp(request: Request, call_next):
    if request.url.path.startswith("/mcp"):
        origin=request.headers.get("origin")
        if origin and settings.origin_allowlist and origin not in settings.origin_allowlist:
            return JSONResponse({"detail":"Origin not allowed"},status_code=403)
        auth=request.headers.get("authorization","")
        if auth != f"Bearer {settings.mcp_api_key}":
            return JSONResponse({"detail":"Unauthorized"},status_code=401)
    return await call_next(request)

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/api/companies")
def companies():
    from app.database import SessionLocal
    from app.repository import list_companies
    with SessionLocal() as db:
        return [{"ticker":c.ticker,"pipeline_type":c.pipeline_type,"status":c.status} for c in list_companies(db)]

app.mount("/mcp",mcp_app)
