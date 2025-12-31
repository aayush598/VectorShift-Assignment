from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
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
    MAX_NODES = 10000
    MAX_EDGES = 50000
    MAX_NODE_ID_LENGTH = 256
    MAX_EDGE_ID_LENGTH = 256
    ENABLE_CACHING = True
    CACHE_TTL = 300
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    RATE_LIMIT_ANONYMOUS = "100/minute"
    RATE_LIMIT_PARSE = "50/minute"

config = Config()

# ============================================================================
# IN-MEMORY CACHE
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
        if len(self.cache) > 1000:
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
    logger.info("🚀 Pipeline Analysis API starting up...")
    logger.info(f"📊 Max nodes: {config.MAX_NODES}, Max edges: {config.MAX_EDGES}")
    logger.info(f"⚡ Cache enabled: {config.ENABLE_CACHING}")
    yield
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

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================================================
# SECURITY MIDDLEWARE
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# ============================================================================
# REQUEST LOGGING MIDDLEWARE
# ============================================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"📥 {request.method} {request.url.path} - Client: {request.client.host}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
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
# PYDANTIC MODELS
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
        node_ids = [node.id for node in v]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Duplicate node IDs detected")
        return v
    
    @validator('edges')
    def validate_edges(cls, v):
        if len(v) > config.MAX_EDGES:
            raise ValueError(f"Pipeline exceeds maximum edge limit of {config.MAX_EDGES}")
        edge_ids = [edge.id for edge in v]
        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError("Duplicate edge IDs detected")
        return v

class PipelineResponse(BaseModel):
    num_nodes: int = Field(..., description="Total number of nodes")
    num_edges: int = Field(..., description="Total number of edges")
    is_dag: bool = Field(..., description="Whether the pipeline is a DAG")
    cycle: Optional[List[str]] = Field(None, description="Cycle path if not DAG")
    cache_hit: bool = Field(default=False, description="Whether result was cached")
    process_time: float = Field(..., description="Processing time in seconds")

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

class MetricsResponse(BaseModel):
    cache_stats: Dict[str, Any]
    config: Dict[str, Any]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def generate_cache_key(pipeline: Pipeline) -> str:
    nodes_str = '|'.join(sorted([f"{n.id}:{n.type}" for n in pipeline.nodes]))
    edges_str = '|'.join(sorted([f"{e.source}->{e.target}" for e in pipeline.edges]))
    cache_input = f"{nodes_str}::{edges_str}"
    return hashlib.sha256(cache_input.encode()).hexdigest()

def analyze_pipeline_graph(pipeline: Pipeline) -> tuple[int, int, bool, Optional[List[str]]]:
    num_nodes = len(pipeline.nodes)
    num_edges = len(pipeline.edges)
    
    if num_nodes == 0:
        return (0, 0, True, None)
    
    node_ids = {node.id for node in pipeline.nodes}
    G = nx.DiGraph()
    G.add_nodes_from(node_ids)
    
    edge_list = []
    for edge in pipeline.edges:
        # Reject self-loops
        if edge.source == edge.target:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Self-loops are not allowed: {edge.source} -> {edge.target}"
            )
        
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
    
    G.add_edges_from(edge_list)
    
    is_dag = nx.is_directed_acyclic_graph(G)
    cycle = None
    
    # If not DAG, find one cycle
    if not is_dag:
        try:
            cycle_edges = nx.find_cycle(G, orientation='original')
            cycle = [edge[0] for edge in cycle_edges]
            # Close the cycle
            if cycle:
                cycle.append(cycle[0])
        except nx.NetworkXNoCycle:
            pass
    
    return (num_nodes, num_edges, is_dag, cycle)

# ============================================================================
# API ENDPOINTS
# ============================================================================
@app.get("/", tags=["Health"])
@limiter.limit(config.RATE_LIMIT_ANONYMOUS)
async def root(request: Request):
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
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="2.0.0"
    )

@app.get("/metrics", response_model=MetricsResponse, tags=["Monitoring"])
@limiter.limit("20/minute")
async def get_metrics(request: Request):
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
    start_time = time.time()
    cache_hit = False
    
    try:
        if config.ENABLE_CACHING:
            cache_key = generate_cache_key(pipeline)
            cached_result = cache.get(cache_key)
            
            if cached_result is not None:
                logger.info(f"✅ Cache hit for pipeline")
                cache_hit = True
                num_nodes, num_edges, is_dag, cycle = cached_result
                process_time = time.time() - start_time
                
                return PipelineResponse(
                    num_nodes=num_nodes,
                    num_edges=num_edges,
                    is_dag=is_dag,
                    cycle=cycle,
                    cache_hit=cache_hit,
                    process_time=process_time
                )
        
        logger.info(f"🔍 Analyzing pipeline: {len(pipeline.nodes)} nodes, {len(pipeline.edges)} edges")
        num_nodes, num_edges, is_dag, cycle = analyze_pipeline_graph(pipeline)
        if config.ENABLE_CACHING:
            cache.set(cache_key, (num_nodes, num_edges, is_dag, cycle))
        
        process_time = time.time() - start_time
        logger.info(f"✅ Analysis complete: DAG={is_dag}, Time={process_time:.3f}s")
        
        return PipelineResponse(
            num_nodes=num_nodes,
            num_edges=num_edges,
            is_dag=is_dag,
            cycle=cycle,
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