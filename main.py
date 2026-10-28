import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from engine import process_and_vault_prompt, restore_ai_response
from database import init_db, log_transaction, get_dashboard_metrics

app = FastAPI(title="GuardRail AI API Gateway")
init_db()

class ProtectRequest(BaseModel):
    prompt: str

class RestoreRequest(BaseModel):
    ai_response: str
    vault: dict

@app.post("/api/protect")
async def protect_endpoint(request: ProtectRequest):
    try:
        clean_text, vault = process_and_vault_prompt(request.prompt)
        log_transaction(request.prompt, clean_text, vault)
        return {"clean_prompt": clean_text, "vault": vault}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/restore")
async def restore_endpoint(request: RestoreRequest):
    try:
        restored_text = restore_ai_response(request.ai_response, request.vault)
        return {"restored_response": restored_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def metrics_endpoint():
    try:
        return get_dashboard_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    try:
        with open("dashboard.html", "r") as file:
            return file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML template missing: {str(e)}")

@app.get("/")
async def root():
    return {"status": "GuardRail AI Server is active"}