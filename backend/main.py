from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
import networkx as nx
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import hashlib
import time

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# RATE LIMITING CONFIGURATION
# ============================================================================
limiter = Limiter(key_func=get_remote_address)

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================
class Config:
    # Graph limits for security
    MAX_NODES = 10000
    MAX_EDGES = 50000
    MAX_NODE_ID_LENGTH = 256
    MAX_EDGE_ID_LENGTH = 256
    
    # Performance
    ENABLE_CACHING = True
    CACHE_TTL = 300  # 5 minutes
    
    # Security
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Add production domains here
    ]
    
    # Rate limiting (requests per minute)
    RATE_LIMIT_ANONYMOUS = "100/minute"
    RATE_LIMIT_PARSE = "50/minute"

config = Config()

# ============================================================================
# IN-MEMORY CACHE (For production, use Redis)
# ============================================================================
class SimpleCache:
    def __init__(self):
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < config.CACHE_TTL:
                self.hits += 1
                return value
            else:
                del self.cache[key]
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any):
        # Limit cache size to prevent memory issues
        if len(self.cache) > 1000:
            # Remove oldest entries
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][1])
            for k, _ in sorted_items[:200]:
                del self.cache[k]
        self.cache[key] = (value, time.time())
    
    def clear(self):
        self.cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{hit_rate:.2f}%"
        }

cache = SimpleCache()

# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Pipeline Analysis API starting up...")
    logger.info(f"📊 Max nodes: {config.MAX_NODES}, Max edges: {config.MAX_EDGES}")
    logger.info(f"⚡ Cache enabled: {config.ENABLE_CACHING}")
    yield
    # Shutdown
    logger.info("🛑 Pipeline Analysis API shutting down...")
    cache.clear()

# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================
app = FastAPI(
    title="Pipeline Analysis API",
    description="Enterprise-grade graph validation and analysis service",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================================================
# SECURITY MIDDLEWARE
# ============================================================================

# CORS - Restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)

# Gzip compression for responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted Host (prevents host header attacks)
# app.add_middleware(
#     TrustedHostMiddleware, 
#     allowed_hosts=["localhost", "127.0.0.1", "yourdomain.com"]
# )

# ============================================================================
# REQUEST/RESPONSE LOGGING MIDDLEWARE
# ============================================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"📥 {request.method} {request.url.path} - Client: {request.client.host}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add performance header
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log response
        logger.info(
            f"📤 {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s"
        )
        
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"❌ {request.method} {request.url.path} - "
            f"Error: {str(e)} - "
            f"Time: {process_time:.3f}s"
        )
        raise

# ============================================================================
# PYDANTIC MODELS WITH VALIDATION
# ============================================================================
class Node(BaseModel):
    id: str = Field(..., description="Unique identifier for the node")
    type: str = Field(..., description="Type of the node")
    data: Dict[str, Any] = Field(default_factory=dict, description="Node metadata")
    
    @validator('id')
    def validate_id(cls, v):
        if len(v) > config.MAX_NODE_ID_LENGTH:
            raise ValueError(f"Node ID exceeds maximum length of {config.MAX_NODE_ID_LENGTH}")
        if not v.strip():
            raise ValueError("Node ID cannot be empty")
        return v
    
    @validator('type')
    def validate_type(cls, v):
        if not v.strip():
            raise ValueError("Node type cannot be empty")
        return v

class Edge(BaseModel):
    id: str = Field(..., description="Unique identifier for the edge")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    
    @validator('id')
    def validate_id(cls, v):
        if len(v) > config.MAX_EDGE_ID_LENGTH:
            raise ValueError(f"Edge ID exceeds maximum length of {config.MAX_EDGE_ID_LENGTH}")
        if not v.strip():
            raise ValueError("Edge ID cannot be empty")
        return v
    
    @validator('source', 'target')
    def validate_node_refs(cls, v):
        if not v.strip():
            raise ValueError("Node reference cannot be empty")
        return v

class Pipeline(BaseModel):
    nodes: List[Node] = Field(..., description="List of pipeline nodes")
    edges: List[Edge] = Field(..., description="List of pipeline edges")
    
    @validator('nodes')
    def validate_nodes(cls, v):
        if len(v) > config.MAX_NODES:
            raise ValueError(f"Pipeline exceeds maximum node limit of {config.MAX_NODES}")
        
        # Check for duplicate node IDs
        node_ids = [node.id for node in v]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Duplicate node IDs detected")
        
        return v
    
    @validator('edges')
    def validate_edges(cls, v):
        if len(v) > config.MAX_EDGES:
            raise ValueError(f"Pipeline exceeds maximum edge limit of {config.MAX_EDGES}")
        
        # Check for duplicate edge IDs
        edge_ids = [edge.id for edge in v]
        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError("Duplicate edge IDs detected")
        
        return v

class PipelineResponse(BaseModel):
    num_nodes: int = Field(..., description="Total number of nodes")
    num_edges: int = Field(..., description="Total number of edges")
    is_dag: bool = Field(..., description="Whether the pipeline is a DAG")
    cache_hit: bool = Field(default=False, description="Whether result was cached")
    process_time: float = Field(..., description="Processing time in seconds")

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime: str

class MetricsResponse(BaseModel):
    cache_stats: Dict[str, Any]
    config: Dict[str, Any]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def generate_cache_key(pipeline: Pipeline) -> str:
    """Generate deterministic cache key from pipeline structure"""
    # Sort nodes and edges for consistency
    nodes_str = '|'.join(sorted([f"{n.id}:{n.type}" for n in pipeline.nodes]))
    edges_str = '|'.join(sorted([f"{e.source}->{e.target}" for e in pipeline.edges]))
    cache_input = f"{nodes_str}::{edges_str}"
    return hashlib.sha256(cache_input.encode()).hexdigest()

def analyze_pipeline_graph(pipeline: Pipeline) -> tuple[int, int, bool]:
    """
    Core graph analysis logic - optimized for performance
    
    Returns:
        tuple: (num_nodes, num_edges, is_dag)
    """
    num_nodes = len(pipeline.nodes)
    num_edges = len(pipeline.edges)
    
    # Empty graph is a DAG
    if num_nodes == 0:
        return (0, 0, True)
    
    # Build node ID set for O(1) lookup
    node_ids = {node.id for node in pipeline.nodes}
    
    # Create directed graph (optimized)
    G = nx.DiGraph()
    
    # Add all nodes at once (faster than one-by-one)
    G.add_nodes_from(node_ids)
    
    # Validate and add edges
    edge_list = []
    for edge in pipeline.edges:
        # Validate edge references
        if edge.source not in node_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Edge references non-existent source node: {edge.source}"
            )
        if edge.target not in node_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Edge references non-existent target node: {edge.target}"
            )
        edge_list.append((edge.source, edge.target))
    
    # Add all edges at once (faster than one-by-one)
    G.add_edges_from(edge_list)
    
    # DAG validation using optimized NetworkX algorithm
    is_dag = nx.is_directed_acyclic_graph(G)
    
    return (num_nodes, num_edges, is_dag)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
@limiter.limit(config.RATE_LIMIT_ANONYMOUS)
async def root(request: Request):
    """Root endpoint - API information"""
    return {
        "service": "Pipeline Analysis API",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/api/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
@limiter.limit(config.RATE_LIMIT_ANONYMOUS)
async def health_check(request: Request):
    """Health check endpoint for monitoring and load balancers"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="2.0.0",
        uptime="N/A"  # In production, calculate from startup time
    )

@app.get("/metrics", response_model=MetricsResponse, tags=["Monitoring"])
@limiter.limit("20/minute")
async def get_metrics(request: Request):
    """Internal metrics endpoint"""
    return MetricsResponse(
        cache_stats=cache.stats(),
        config={
            "max_nodes": config.MAX_NODES,
            "max_edges": config.MAX_EDGES,
            "cache_enabled": config.ENABLE_CACHING,
            "cache_ttl": config.CACHE_TTL
        }
    )

@app.post(
    "/pipelines/parse",
    response_model=PipelineResponse,
    tags=["Pipeline"],
    status_code=status.HTTP_200_OK
)
@limiter.limit(config.RATE_LIMIT_PARSE)
async def parse_pipeline(request: Request, pipeline: Pipeline):
    """
    Analyze pipeline structure and validate graph properties.
    
    **Features:**
    - Node and edge counting
    - DAG validation (cycle detection)
    - Structural validation
    - Result caching for performance
    - Rate limiting for protection
    
    **Limits:**
    - Max nodes: 10,000
    - Max edges: 50,000
    - Rate limit: 50 requests/minute per IP
    
    **Security:**
    - Input validation
    - Size limits
    - Duplicate detection
    - Reference validation
    """
    start_time = time.time()
    cache_hit = False
    
    try:
        # Check cache first
        if config.ENABLE_CACHING:
            cache_key = generate_cache_key(pipeline)
            cached_result = cache.get(cache_key)
            
            if cached_result is not None:
                logger.info(f"✅ Cache hit for pipeline")
                cache_hit = True
                num_nodes, num_edges, is_dag = cached_result
                process_time = time.time() - start_time
                
                return PipelineResponse(
                    num_nodes=num_nodes,
                    num_edges=num_edges,
                    is_dag=is_dag,
                    cache_hit=cache_hit,
                    process_time=process_time
                )
        
        # Analyze pipeline
        logger.info(f"🔍 Analyzing pipeline: {len(pipeline.nodes)} nodes, {len(pipeline.edges)} edges")
        num_nodes, num_edges, is_dag = analyze_pipeline_graph(pipeline)
        
        # Cache result
        if config.ENABLE_CACHING:
            cache.set(cache_key, (num_nodes, num_edges, is_dag))
        
        process_time = time.time() - start_time
        logger.info(f"✅ Analysis complete: DAG={is_dag}, Time={process_time:.3f}s")
        
        return PipelineResponse(
            num_nodes=num_nodes,
            num_edges=num_edges,
            is_dag=is_dag,
            cache_hit=cache_hit,
            process_time=process_time
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"⚠️ Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during pipeline analysis"
        )

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# ============================================================================
# STARTUP MESSAGE
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )