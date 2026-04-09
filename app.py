from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import asyncio
from scraper import run_scraper
import json

app = FastAPI(title="电商商品价格自动化采集与对比工具")

templates = Jinja2Templates(directory="templates")

class SearchRequest(BaseModel):
    keyword: str
    use_mock: bool = True

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/search")
async def search_api(req: SearchRequest):
    data = await run_scraper(req.keyword, use_mock=req.use_mock)
    return {"status": "success", "data": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
