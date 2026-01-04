# app/models/pipeline.py

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from app.core.config import settings


# ===============================
# CORE ENTITIES
# ===============================

class Node(BaseModel):
    id: str = Field(..., description="Unique identifier for the node")
    type: str = Field(..., description="Node type")
    data: Dict[str, Any] = Field(default_factory=dict)

    @validator("id")
    def validate_id(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Node ID cannot be empty")
        if len(v) > settings.MAX_NODE_ID_LENGTH:
            raise ValueError(
                f"Node ID exceeds max length {settings.MAX_NODE_ID_LENGTH}"
            )
        return v

    @validator("type")
    def validate_type(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Node type cannot be empty")
        return v


class Edge(BaseModel):
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None

    @validator("source", "target")
    def validate_refs(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Edge references cannot be empty")
        return v


# ===============================
# PIPELINE REQUEST
# ===============================

class Pipeline(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

    @validator("nodes")
    def validate_nodes(cls, nodes: List[Node]) -> List[Node]:
        if nodes is None:
            raise ValueError("nodes must be provided")

        if len(nodes) > settings.MAX_NODES:
            raise ValueError(
                f"Pipeline exceeds max nodes ({settings.MAX_NODES})"
            )

        ids = [n.id for n in nodes]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate node IDs detected")

        return nodes

    @validator("edges")
    def validate_edges(cls, edges: List[Edge]) -> List[Edge]:
        if edges is None:
            raise ValueError("edges must be provided")

        if len(edges) > settings.MAX_EDGES:
            raise ValueError(
                f"Pipeline exceeds max edges ({settings.MAX_EDGES})"
            )

        return edges


# ===============================
# PIPELINE RESPONSE
# ===============================

class PipelineResponse(BaseModel):
    num_nodes: int = Field(..., description="Total number of nodes")
    num_edges: int = Field(..., description="Total number of edges")
    is_dag: bool = Field(..., description="Whether pipeline is a DAG")
    cycle: Optional[List[str]] = Field(
        None,
        description="Cycle path if graph is not a DAG"
    )
    cache_hit: bool = Field(
        default=False,
        description="Whether response was served from cache"
    )
    process_time: float = Field(
        ...,
        description="Processing time in seconds"
    )
