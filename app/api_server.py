"""
Decoupled Local REST API Service for Tiny SQL Language Model (SQL-SLM).
Includes AK-nice-* API Key Authentication, OpenAI-compatible chat completions,
autonomous multi-database execution, and key management endpoints.
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, Security, Depends, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

from inference.generate import TinyLLMInference
from agent_engine.agent import SQLAgent
from agent_engine.db_sandbox import EnterpriseDBSandbox
from agent_engine.schema_formatter import SchemaFormatter
from evaluation.evaluate_sql import SQLEvaluator
from app.key_manager import APIKeyManager

app = FastAPI(
    title="Tiny SQL Language Model (SQL-SLM) API",
    version="1.2.0",
    description="Private Local Inference & Multi-Database Text-to-SQL API Service with AK-nice-* API Key Security."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication Handler
security_bearer = HTTPBearer(auto_error=False)
key_manager = APIKeyManager()

def verify_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> Dict[str, Any]:
    """
    Validates the AK-nice-* API Key from either:
    1. 'Authorization: Bearer AK-nice-...'
    2. 'X-API-Key: AK-nice-...'
    """
    token = None
    if credentials:
        token = credentials.credentials
    elif x_api_key:
        token = x_api_key

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key. Please provide a valid 'AK-nice-...' key in 'Authorization: Bearer <KEY>' or 'X-API-Key: <KEY>' header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    key_meta = key_manager.validate_and_record_use(token)
    if not key_meta:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API Key. Key must be an active 'AK-nice-...' token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return key_meta

# Lazy singletons
_bot: Optional[TinyLLMInference] = None
_agent: Optional[SQLAgent] = None
_evaluator: Optional[SQLEvaluator] = None
_sandbox: Optional[EnterpriseDBSandbox] = None

def get_bot() -> TinyLLMInference:
    global _bot
    if _bot is None:
        _bot = TinyLLMInference()
    return _bot

def get_agent() -> SQLAgent:
    global _agent
    if _agent is None:
        _agent = SQLAgent()
    return _agent

def get_evaluator() -> SQLEvaluator:
    global _evaluator
    if _evaluator is None:
        _evaluator = SQLEvaluator()
    return _evaluator

def get_sandbox() -> EnterpriseDBSandbox:
    global _sandbox
    if _sandbox is None:
        _sandbox = EnterpriseDBSandbox()
    return _sandbox

# Request & Response Models
class CreateKeyRequest(BaseModel):
    client_name: str = Field("External Application", description="Name or identifier of the client application")
    prefix: Optional[str] = Field("AK-nice-", description="Prefix for the generated key")

class RevokeKeyRequest(BaseModel):
    key_id: str = Field(..., description="ID of the key to revoke")

class GenerateSQLRequest(BaseModel):
    question: str = Field(..., description="Natural language question, e.g. 'Show top 5 customers by spend'")
    schema_text: Optional[str] = Field(None, description="Optional custom schema in compact format, DDL, or XML")
    dialect: Optional[str] = Field("postgres", description="Target SQL dialect (postgres, tsql, sqlite)")
    temperature: float = Field(0.0, ge=0.0, le=1.0, description="Sampling temperature (0.0 for greedy deterministic)")
    max_new_tokens: int = Field(140, ge=16, le=512)

class AgentQueryRequest(BaseModel):
    prompt: str = Field(..., description="Natural language database query")
    connection_uri: Optional[str] = Field(None, description="Optional database URI (e.g. postgresql+psycopg2://user:pass@host:5432/db)")
    schema_text: Optional[str] = Field(None, description="Optional custom DDL schema")
    max_retries: int = Field(2, ge=0, le=5, description="Self-repair retry attempts")

class EvaluateRequest(BaseModel):
    generated_sql: str
    ground_truth_sql: str
    ordered: bool = False

# OpenAI-Compatible Format
class OpenAIChatMessage(BaseModel):
    role: str
    content: str

class OpenAIChatRequest(BaseModel):
    model: Optional[str] = "tiny-sql-slm"
    messages: List[OpenAIChatMessage]
    temperature: Optional[float] = 0.1
    max_tokens: Optional[int] = 140

# --- Public Endpoints ---
@app.get("/health")
def health_check():
    bot = get_bot()
    return {
        "status": "healthy",
        "service": "Tiny-SQL-SLM",
        "auth_format": "AK-nice-*",
        "device": bot.device,
        "vocab_size": bot.tokenizer.vocab_size,
        "max_seq_len": bot.config.max_seq_len,
        "version": "1.2.0"
    }

# --- API Key Management Endpoints ---
@app.post("/v1/keys/create")
def create_new_api_key(req: CreateKeyRequest):
    """Generates a new secure 'AK-nice-...' API key for external client usage."""
    new_key = key_manager.create_key(client_name=req.client_name, prefix=req.prefix)
    return {
        "success": True,
        "message": "API key generated successfully. Save this key; you will need it for Authorization headers.",
        "key_id": new_key["key_id"],
        "api_key": new_key["api_key"],
        "client_name": new_key["client_name"],
        "created_at": new_key["created_at"]
    }

@app.get("/v1/keys/list")
def list_api_keys(auth: Dict[str, Any] = Depends(verify_api_key)):
    """Lists registered API keys and usage statistics."""
    return {
        "keys": key_manager.list_keys()
    }

@app.post("/v1/keys/revoke")
def revoke_api_key(req: RevokeKeyRequest, auth: Dict[str, Any] = Depends(verify_api_key)):
    """Revokes an active API key."""
    success = key_manager.revoke_key(req.key_id)
    if not success:
        raise HTTPException(status_code=404, detail="Key ID not found.")
    return {"success": True, "message": f"Key {req.key_id} has been revoked."}

# --- Protected Inference & SQL Endpoints ---
@app.get("/v1/schema")
def get_database_schema(
    connection_uri: Optional[str] = None,
    auth: Dict[str, Any] = Depends(verify_api_key)
):
    """Introspects and returns database schema."""
    try:
        if connection_uri:
            sandbox = EnterpriseDBSandbox(connection_uri=connection_uri)
            catalog = SchemaFormatter.extract_from_sqlalchemy(sandbox.engine)
        else:
            sandbox = get_sandbox()
            catalog = SchemaFormatter.extract_from_sqlite(sandbox.db_path)
            
        return {
            "compact": SchemaFormatter.to_compact(catalog),
            "table_count": len(catalog.tables),
            "tables": {t.name: [c.name for c in t.columns] for t in catalog.tables.values()}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/generate_sql")
def generate_sql(
    req: GenerateSQLRequest,
    auth: Dict[str, Any] = Depends(verify_api_key)
):
    """Generates pure SQL query from natural language with schema conditioning (Protected with AK-nice-* key)."""
    bot = get_bot()
    try:
        res = bot.generate_structured(
            question=req.question,
            schema=req.schema_text,
            dialect=req.dialect,
            max_new_tokens=req.max_new_tokens,
            temperature=req.temperature
        )
        return {
            **res,
            "authenticated_as": auth.get("client_name")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/agent/query")
def run_agent_query(
    req: AgentQueryRequest,
    auth: Dict[str, Any] = Depends(verify_api_key)
):
    """Autonomous Text-to-SQL Agent: Generates, Validates AST, Executes on DB & Explains (Protected with AK-nice-* key)."""
    agent = get_agent()
    try:
        if req.connection_uri:
            sandbox = EnterpriseDBSandbox(connection_uri=req.connection_uri)
            agent.set_database(sandbox)
        elif req.schema_text:
            agent.set_custom_schema_text(req.schema_text)
            
        agent_res = agent.run(user_prompt=req.prompt, max_retries=req.max_retries)
        return {
            **agent_res,
            "authenticated_as": auth.get("client_name")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/chat/completions")
def openai_chat_completions(
    req: OpenAIChatRequest,
    auth: Dict[str, Any] = Depends(verify_api_key)
):
    """OpenAI API-compatible chat endpoint (Accepts AK-nice-* keys in Authorization header)."""
    agent = get_agent()
    user_msg = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
    if not user_msg:
        raise HTTPException(status_code=400, detail="No user message found.")
        
    try:
        res = agent.run(user_prompt=user_msg)
        sql = res.get("generated_sql", "")
        reply_content = f"```sql\n{sql}\n```\n\n{res.get('explanation', '')}"
        
        return {
            "id": f"chatcmpl-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": reply_content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(user_msg.split()),
                "completion_tokens": len(reply_content.split()),
                "total_tokens": len(user_msg.split()) + len(reply_content.split())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/evaluate")
def evaluate_sql_equivalence(
    req: EvaluateRequest,
    auth: Dict[str, Any] = Depends(verify_api_key)
):
    evaluator = get_evaluator()
    try:
        res = evaluator.evaluate_semantic_equivalence(
            generated_sql=req.generated_sql,
            ground_truth_sql=req.ground_truth_sql,
            ordered=req.ordered
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("[*] Starting Tiny SQL-SLM API Server on http://0.0.0.0:8000 (accessible across LAN)...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
