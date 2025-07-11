"""GUARDRIVE API - Servidor Principal

Servidor FastAPI robusto com monitoramento de saúde,
middleware de segurança e integração simbiótica.
"""

import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import local modules
try:
    from .core.config import settings
    from .core.logger import setup_logger
    from .middleware.error_handler import error_handler_middleware
    from .routers import agentes, telemetria, configuracao, websocket
except ImportError:
    # Fallback para desenvolvimento
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logger = setup_logger() if 'setup_logger' in globals() else logging.getLogger(__name__)
    logger.info("🚀 GUARDRIVE API iniciando...")
    
    # Verificar dependências críticas
    try:
        # Redis connection test
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        logger.info("✅ Redis conectado")
    except Exception as e:
        logger.warning(f"⚠️ Redis indisponível: {e}")
    
    yield
    
    # Shutdown
    logger.info("🔄 GUARDRIVE API finalizando...")


# Criar aplicação FastAPI
app = FastAPI(
    title="GUARDRIVE API",
    description="Enterprise-grade AI orchestration platform with symbiotic intelligence",
    version="1.0.2",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure adequadamente em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de compressão
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware customizado de tratamento de erros
if 'error_handler_middleware' in globals():
    app.middleware("http")(error_handler_middleware)


@app.get("/", tags=["Core"])
async def root() -> Dict[str, Any]:
    """Endpoint raiz com informações do sistema"""
    return {
        "message": "GUARDRIVE API - Operational",
        "version": "1.0.2",
        "status": "healthy",
        "features": [
            "symbiotic-intelligence",
            "ai-orchestration", 
            "blockchain-integration",
            "real-time-monitoring"
        ]
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint para monitoramento"""
    return {
        "status": "healthy",
        "timestamp": os.environ.get('TIMESTAMP', 'unknown'),
        "version": "1.0.2",
        "environment": os.environ.get('ENVIRONMENT', 'development')
    }


@app.get("/metrics", tags=["Monitoring"])
async def metrics() -> Dict[str, Any]:
    """Métricas básicas do sistema"""
    import psutil
    
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
        "uptime": "unknown"  # Implementar cálculo de uptime
    }


# Incluir routers se disponíveis
try:
    if 'agentes' in globals():
        app.include_router(agentes.router, prefix="/api/v1/agentes", tags=["Agentes"])
    if 'telemetria' in globals():
        app.include_router(telemetria.router, prefix="/api/v1/telemetria", tags=["Telemetria"])
    if 'configuracao' in globals():
        app.include_router(configuracao.router, prefix="/api/v1/config", tags=["Configuração"])
    if 'websocket' in globals():
        app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
except Exception as e:
    print(f"⚠️ Erro ao incluir routers: {e}")


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Handler customizado para 404"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Resource not found",
            "path": str(request.url.path),
            "method": request.method
        }
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc: Exception):
    """Handler customizado para erros 500"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    # Configuração para desenvolvimento
    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"🚀 Iniciando GUARDRIVE API em http://{host}:{port}")
    
    uvicorn.run(
        "src.api.main:app" if __name__ != "__main__" else "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        access_log=True
    )

