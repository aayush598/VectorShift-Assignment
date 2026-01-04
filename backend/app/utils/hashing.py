# app/utils/hashing.py

import hashlib
from app.models.pipeline import Pipeline


def generate_cache_key(pipeline: Pipeline) -> str:
    """
    Generate a deterministic hash for a pipeline definition.
    Ensures identical pipelines always produce the same cache key,
    regardless of node or edge ordering.
    """

    nodes_str = "|".join(
        sorted(f"{node.id}:{node.type}" for node in pipeline.nodes)
    )

    edges_str = "|".join(
        sorted(
            f"{edge.source}:{edge.sourceHandle}"
            f"->{edge.target}:{edge.targetHandle}"
            for edge in pipeline.edges
        )
    )

    cache_input = f"{nodes_str}::{edges_str}"

    return hashlib.sha256(cache_input.encode("utf-8")).hexdigest()
