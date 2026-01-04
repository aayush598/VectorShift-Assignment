# app/services/pipeline_analyzer.py

from typing import Optional, List, Tuple
import networkx as nx
from fastapi import HTTPException
from app.models.pipeline import Pipeline


def analyze_pipeline(
    pipeline: Pipeline
) -> Tuple[int, int, bool, Optional[List[str]]]:
    """
    Analyze pipeline graph structure.

    Returns:
        (num_nodes, num_edges, is_dag, cycle_path)
    """

    num_nodes = len(pipeline.nodes)
    num_edges = len(pipeline.edges)

    if num_nodes == 0:
        return 0, 0, True, None

    node_ids = {node.id for node in pipeline.nodes}

    graph = nx.MultiDiGraph()
    graph.add_nodes_from(node_ids)

    for edge in pipeline.edges:
        if edge.source == edge.target:
            raise HTTPException(
                status_code=400,
                detail=f"Self-loop detected on node '{edge.source}'"
            )

        if edge.source not in node_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown source node '{edge.source}'"
            )

        if edge.target not in node_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown target node '{edge.target}'"
            )

        graph.add_edge(
            edge.source,
            edge.target,
            sourceHandle=edge.sourceHandle,
            targetHandle=edge.targetHandle,
        )

    try:
        cycle_edges = nx.find_cycle(graph, orientation="original")
        cycle = [edge[0] for edge in cycle_edges]
        cycle.append(cycle_edges[0][0])
        return num_nodes, num_edges, False, cycle

    except nx.NetworkXNoCycle:
        return num_nodes, num_edges, True, None
